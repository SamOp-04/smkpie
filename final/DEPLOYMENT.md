# SMKpie Deployment Guide

## ⚠️ Breaking Changes from Previous Version

This update includes significant improvements to the SMKpie anomaly detection API. Please follow this deployment guide carefully to ensure a smooth upgrade.

---

## 🔄 What Changed

### 1. **Database Schema Updates** (CRITICAL)
- Added 4 new tables: `predictions`, `alerts`, `api_logs`, `performance_metrics`
- Added `notification_channels` column to `monitor_settings`
- **Action Required**: Run SQL schema updates before deploying

### 2. **Dependency Updates**
- Upgraded `redis` from 4.1.0 → 5.0.0 with asyncio support
- Added `httpx` for async HTTP requests
- **Action Required**: Rebuild Docker images with new requirements

### 3. **New Services**
- Added Celery Beat scheduler for background tasks
- **Action Required**: Deploy celery-beat alongside celery-worker

### 4. **Architecture Changes**
- ModelManager now uses singleton pattern (loads once, not per request)
- Redis operations are fully async (no more event loop blocking)
- Input validation now enforces 18 required network features
- All predictions/alerts persisted to database

---

## 📋 Pre-Deployment Checklist

- [ ] Backup your Supabase database
- [ ] Review the new database schema in `scripts/supabase_schema.sql`
- [ ] Ensure you have the required environment variables (see below)
- [ ] Rebuild Docker images with updated dependencies
- [ ] Have access to aws-cli to push image to ECR/ECS

---

## 🗄️ Step 1: Apply Database Schema

### Option A: Manual (Supabase Dashboard)

1. Open Supabase SQL Editor: https://app.supabase.com/project/YOUR_PROJECT/sql
2. Copy the contents of `final/scripts/supabase_schema.sql`
3. Run the SQL script
4. Verify all tables created:
   ```sql
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'public'
   AND table_type = 'BASE TABLE';
   ```

### Option B: Automated Container Job

Run the migration-check script in your container runtime to validate table existence:

```bash
python scripts/apply_schema_updates.py
```

Expected output:
```
✓ EXISTS: users
✓ EXISTS: monitor_settings
✓ EXISTS: model_versions
✓ EXISTS: predictions
✓ EXISTS: alerts
✓ EXISTS: api_logs
✓ EXISTS: performance_metrics
```

---

## 🐳 Step 2: Local Development (Docker Compose)

### Build and Start Services

```bash
cd final

# Build new image with updated dependencies
docker-compose build

# Start all services (API, Redis, Celery Worker, Celery Beat)
docker-compose up -d

# Verify all containers running
docker-compose ps
```

Expected containers:
- `final-api-1` - FastAPI application
- `final-redis-1` - Redis server
- `final-worker-1` - Celery worker
- `final-beat-1` - Celery beat scheduler (NEW)

### Check Logs

```bash
# API startup logs
docker-compose logs api

# Should see:
# ✓ Redis connection OK
# ✓ RedisActionExecutor enabled
# ✓ Model assets preloaded successfully
# 🚀 Welcome to SMKpie!

# Celery beat logs
docker-compose logs beat

# Should see scheduled tasks:
# celery beat v5.2.3 is starting.
# Scheduler: Sending due task check-model-performance-daily
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Test prediction (all 18 features required)
curl -X POST http://localhost:8000/predict/YOUR_API_KEY \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

`test_payload.json`:
```json
{
  "Flow Duration": 120.5,
  "Total Fwd Packet": 10,
  "Total Bwd Packets": 5,
  "Fwd Packets/s": 0.5,
  "Bwd Packets/s": 0.25,
  "Flow Packets/s": 0.75,
  "Fwd Header Length": 200,
  "Bwd Header Length": 100,
  "Fwd Packet Length Mean": 512.0,
  "Bwd Packet Length Mean": 256.0,
  "Packet Length Mean": 384.0,
  "Packet Length Std": 128.0,
  "Flow IAT Mean": 50.0,
  "Flow IAT Std": 10.0,
  "Active Mean": 100.0,
  "Idle Mean": 50.0,
  "FWD Init Win Bytes": 8192,
  "Bwd Init Win Bytes": 4096
}
```

Response (now includes prediction_id and timestamp):
```json
{
  "anomaly": false,
  "score": 0.23,
  "recommended_action": "allow",
  "prediction_id": 1,
  "timestamp": "2026-03-20T12:34:56.789"
}
```

---

## ☁️ Step 3: AWS/ECS Production Deployment

### Prerequisites

```bash
# Login to AWS ECR
aws ecr get-login-password --region ap-south-1 | \
  docker login --username AWS --password-stdin \
  371601828313.dkr.ecr.ap-south-1.amazonaws.com

# Ensure ECS cluster exists
aws ecs describe-clusters --region ap-south-1 --clusters smkpie-cluster

# Create cluster if missing
aws ecs create-cluster --region ap-south-1 --cluster-name smkpie-cluster
```

### Build and Push Updated Image

```bash
cd final

# Build image with new dependencies
docker build -t smkpie-runtime:next .

# Tag for ECR
docker tag smkpie-runtime:next \
  371601828313.dkr.ecr.ap-south-1.amazonaws.com/smkpie-runtime:next

# Push to ECR
docker push 371601828313.dkr.ecr.ap-south-1.amazonaws.com/smkpie-runtime:next
```

### Configure ECS Task Definitions

Edit these files and replace placeholders (`<ACCOUNT_ID>`, `<ELASTICACHE_ENDPOINT>`, `<S3_BUCKET>`, SMTP values):
- `infrastructure/ecs/taskdef-api.json`
- `infrastructure/ecs/taskdef-celery-worker.json`
- `infrastructure/ecs/taskdef-celery-beat.json`

If using `:next`, update image in task definition JSON files:
```json
"image": "371601828313.dkr.ecr.ap-south-1.amazonaws.com/smkpie-runtime:next"
```

Create ECS services once using `infrastructure/ecs/SERVICE_BOOTSTRAP.md` if they do not exist yet.

Or tag as `:latest` once tested:
```bash
docker tag smkpie-runtime:next \
  371601828313.dkr.ecr.ap-south-1.amazonaws.com/smkpie-runtime:latest

docker push 371601828313.dkr.ecr.ap-south-1.amazonaws.com/smkpie-runtime:latest
```

### Store Secrets in SSM Parameter Store

```bash
aws ssm put-parameter --region ap-south-1 --name /smkpie/SUPABASE_URL --type SecureString --value "https://..." --overwrite
aws ssm put-parameter --region ap-south-1 --name /smkpie/SUPABASE_KEY --type SecureString --value "..." --overwrite
aws ssm put-parameter --region ap-south-1 --name /smkpie/SUPABASE_SERVICE_ROLE_KEY --type SecureString --value "..." --overwrite
aws ssm put-parameter --region ap-south-1 --name /smkpie/SUPABASE_JWT_SECRET --type SecureString --value "..." --overwrite
aws ssm put-parameter --region ap-south-1 --name /smkpie/REDIS_PASSWORD --type SecureString --value "..." --overwrite
aws ssm put-parameter --region ap-south-1 --name /smkpie/AWS_ACCESS_KEY_ID --type SecureString --value "..." --overwrite
aws ssm put-parameter --region ap-south-1 --name /smkpie/AWS_SECRET_ACCESS_KEY --type SecureString --value "..." --overwrite
aws ssm put-parameter --region ap-south-1 --name /smkpie/SMTP_USER --type SecureString --value "..." --overwrite
aws ssm put-parameter --region ap-south-1 --name /smkpie/SMTP_PASSWORD --type SecureString --value "..." --overwrite
```

### Deploy to ECS

```bash
# 1. Register task definition revisions + force service rollout
powershell -ExecutionPolicy Bypass -File infrastructure/ecs/deploy-ecs.ps1 \
  -Region ap-south-1 \
  -Cluster smkpie-cluster \
  -ApiService smkpie-api-svc \
  -WorkerService smkpie-celery-worker-svc \
  -BeatService smkpie-celery-beat-svc

# 2. Watch deployment state
aws ecs describe-services --region ap-south-1 --cluster smkpie-cluster \
  --services smkpie-api-svc smkpie-celery-worker-svc smkpie-celery-beat-svc \
  --query "services[].{name:serviceName,status:status,running:runningCount,desired:desiredCount,pending:pendingCount}"
```

### Verify ECS Deployment

```bash
# Check ECS tasks
aws ecs list-tasks --region ap-south-1 --cluster smkpie-cluster --service-name smkpie-api-svc
aws ecs list-tasks --region ap-south-1 --cluster smkpie-cluster --service-name smkpie-celery-worker-svc
aws ecs list-tasks --region ap-south-1 --cluster smkpie-cluster --service-name smkpie-celery-beat-svc

# Check API logs in CloudWatch Logs
aws logs tail /ecs/smkpie-api --region ap-south-1 --follow

# Should see:
# ✓ Redis connection OK
# ✓ RedisActionExecutor enabled
# ✓ Model assets preloaded successfully
# 🚀 Welcome to SMKpie!

# Check Celery Beat logs
aws logs tail /ecs/smkpie-celery-beat --region ap-south-1 --follow

# Should see scheduled tasks registered:
# Scheduler: Sending due task check-model-performance-daily
```

---

## 🔐 Environment Variables

### Required Variables

Use `environment` and `secrets` blocks in the ECS task definitions under `infrastructure/ecs/`.
All sensitive values should be stored in SSM Parameter Store (`SecureString`) and referenced via `valueFrom`.

---

## ✅ Post-Deployment Verification

### 1. Database Tables Exist

```sql
-- Run in Supabase SQL Editor
SELECT COUNT(*) FROM predictions;
SELECT COUNT(*) FROM alerts;
SELECT COUNT(*) FROM api_logs;
SELECT COUNT(*) FROM performance_metrics;
```

### 2. API Responds

```bash
# Get ALB DNS name from ECS service target group/load balancer
aws ecs describe-services --region ap-south-1 --cluster smkpie-cluster --services smkpie-api-svc

# Test health endpoint
curl https://your-domain.com/health

# Test prediction (use valid token + API key)
curl -X POST https://your-domain.com/predict/YOUR_API_KEY \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

### 3. Predictions Persisted

```sql
-- Check latest predictions
SELECT id, score, is_anomaly, recommended_action, timestamp
FROM predictions
ORDER BY timestamp DESC
LIMIT 10;
```

### 4. Background Tasks Running

```bash
# Check Celery beat logs (should show scheduled tasks)
aws logs tail /ecs/smkpie-celery-beat --region ap-south-1 --follow

# Look for:
# Scheduler: Sending due task check-model-performance-daily
# Scheduler: Sending due task evaluate-retraining-weekly
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'redis.asyncio'"

**Solution**: Rebuild Docker image with updated `requirements.docker.txt`:
```bash
docker build --no-cache -t smkpie-runtime:next .
```

### Issue: "Table 'predictions' does not exist"

**Solution**: Run database migration:
```bash
# Local
python scripts/apply_schema_updates.py

# ECS task/container
python scripts/apply_schema_updates.py
```

### Issue: "Celery beat not scheduling tasks"

**Check**:
```bash
# Verify beat service is running
aws ecs describe-services --region ap-south-1 --cluster smkpie-cluster --services smkpie-celery-beat-svc

# Check beat logs for errors
aws logs tail /ecs/smkpie-celery-beat --region ap-south-1 --follow
```

### Issue: "ValidationError: 18 fields required"

**Cause**: New input validation requires all 18 network traffic features.

**Solution**: Update API clients to include all required fields (see test_payload.json above).

### Issue: "Model not found at model_storage/model.pt"

**Solution**: Train model or copy model files into Docker image:
```bash
# Option 1: Train model
cd final
python -m ml.training.train --data-path data/processed/csecicids2018_model_ready.csv

# Option 2: Model should be in model_storage/ during Docker build
# Verify .dockerignore doesn't exclude model_storage/
```

---

## 📊 Monitoring

### Key Metrics to Track

1. **Prediction Latency**
   ```sql
   SELECT AVG(processing_time_ms) as avg_latency_ms
   FROM predictions
   WHERE timestamp > now() - interval '1 hour';
   ```

2. **Anomaly Rate**
   ```sql
   SELECT
     COUNT(*) FILTER (WHERE is_anomaly) * 100.0 / COUNT(*) as anomaly_rate_percent
   FROM predictions
   WHERE timestamp > now() - interval '1 day';
   ```

3. **Alert Success Rate**
   ```sql
   SELECT
     alert_type,
     COUNT(*) FILTER (WHERE status = 'sent') * 100.0 / COUNT(*) as success_rate
   FROM alerts
   WHERE timestamp > now() - interval '1 day'
   GROUP BY alert_type;
   ```

4. **Blocked/Throttled API Keys**
   ```bash
  # Check Redis (ElastiCache or reachable Redis endpoint)
  redis-cli -h <ELASTICACHE_ENDPOINT> -a <REDIS_PASSWORD>
   > KEYS blocked:*
   > KEYS throttled:*
   ```

---

## 🔄 Rollback Plan

If issues arise, rollback to previous version:

```bash
# ECS: force service to use previous task definition revision
aws ecs update-service --region ap-south-1 --cluster smkpie-cluster --service smkpie-api-svc --task-definition smkpie-api:<PREVIOUS_REV>
aws ecs update-service --region ap-south-1 --cluster smkpie-cluster --service smkpie-celery-worker-svc --task-definition smkpie-celery-worker:<PREVIOUS_REV>
aws ecs update-service --region ap-south-1 --cluster smkpie-cluster --service smkpie-celery-beat-svc --task-definition smkpie-celery-beat:<PREVIOUS_REV>

# Docker Compose: Use previous image tag
docker-compose down
docker-compose pull  # Pull previous images
docker-compose up -d
```

**Note**: Database schema changes are forward-compatible. New tables won't break old code.

---

## 📞 Support

If you encounter issues:
1. Check logs: `aws logs tail /ecs/smkpie-api --region ap-south-1 --follow`
2. Verify schema: `python scripts/apply_schema_updates.py`
3. Test locally first: `docker-compose up`
4. Review this guide for missed steps

---

## ✨ What's New - Feature Summary

✅ **Input Validation** - All 18 network features validated
✅ **Database Persistence** - Predictions, alerts, logs saved
✅ **Action Enforcement** - Block/throttle actually works via Redis
✅ **Unified Notifications** - Webhook, email, realtime support
✅ **Background Tasks** - Daily performance checks, weekly retraining
✅ **Async Redis** - No more event loop blocking
✅ **Singleton Model** - Loaded once, not per request
✅ **Performance Tracking** - Processing time recorded per prediction

**Result**: Production-ready anomaly detection API! 🎉
