# SMKpie

SMKpie is a FastAPI-based cybersecurity anomaly-detection backend intended to be embedded behind a web app or gateway. It scores traffic-like feature payloads, recommends an action, and can emit alert hooks.

Current stack highlights:

- API endpoints for auth, prediction, health, logs, and settings.
- PyTorch-based model training and serving.
- Background processing with Celery.
- Infrastructure definitions for Docker, Kubernetes, and Terraform.
- Test coverage for integration and unit scenarios.

## Repository Layout

Top-level workspace files:

- `pip.ini`: local pip configuration.
- `pyvenv.cfg`: Python environment metadata.
- `README.md`: this document.
- `final/`: main application source tree.

## `final/` Application Structure

### Runtime Entry Points

- `main.py`: FastAPI app setup, middleware, route registration, lifecycle hooks.
- `celery_app.py`: Celery worker app configuration.
- `tasks.py`: background task definitions.

### Containerization

- `Dockerfile`: optimized runtime image build for the API.
- `docker-compose.yml`: local multi-service orchestration.
- `requirements.txt`: base Python dependencies.
- `requirements.docker.txt`: container-focused dependencies (CPU torch index).
- `.dockerignore`: excludes local data/models/venvs and build noise from image context.

### API Layer (`api/`)

- `versioning.py`: API versioning helpers.
- `dependencies/`
	- `auth_deps.py`: auth dependency wiring.
	- `custom_exceptions.py`: API-specific exceptions.
- `routes/`
	- `admin.py`: administrative routes.
	- `auth.py`: authentication/token routes.
	- `health.py`: health and readiness endpoints.
	- `logs.py`: log retrieval/inspection endpoints.
	- `model_metrics.py`: model metric endpoints.
	- `predict.py`: prediction endpoint.
	- `settings.py`: runtime/config related routes.

### Core Application Services (`core/`)

- `config.py`: settings model and environment-backed configuration.
- `utils.py`: shared utility helpers.
- `database/`
	- `redis_manager.py`: Redis connection pooling.
	- `supabase.py`: Supabase client setup.
	- `supabase_crud.py`: Supabase CRUD operations.
- `middleware/`
	- `logging.py`: request/response logging middleware.
- `schemas/`
	- `models.py`: shared Pydantic/domain schemas.
- `security/`
- 	`action_executor.py`: pluggable action execution hook for host app integrations.
	- `auth.py`: auth logic.
	- `rate_limiter.py`: request throttling utilities.
	- `request_validator.py`: request validation controls.

### Data Processing (`data_processing/`)

- `collectors/`
	- `api_logs.py`: API log ingestion helpers.
	- `web_traffic.py`: web traffic collection logic.
- `transformers/`
	- `drift_detector.py`: data/model drift checks.
- `validation/`
	- `schemas.py`: validation schemas for data flows.

### Machine Learning (`ml/`)

- `evaluation/`
	- `validator.py`: model evaluation/validation logic.
- `monitoring/`
	- `performance.py`: live model performance monitoring.
	- `retrain.py`: retraining orchestration hooks.
- `serving/`
	- `model_manager.py`: loads `model.pt` + preprocessor, supports local/S3 model updates.
	- `predictor.py`: framework-agnostic scoring helper (PyTorch/legacy-compatible path).
	- `preprocessor.py`: feature preprocessing and scaler persistence.
- `training/`
	- `hyperparams.yaml`: training hyperparameters.
	- `train.py`: PyTorch training pipeline with CUDA auto-detection.
- `versioning/`
	- `model_version.py`: model version metadata/management.

### Model Artifacts (`model_storage/`)

- `model.pt`: serialized PyTorch model checkpoint.
- `evaluation_metrics.json`: latest evaluation output from training.
- `preprocessor.joblib`: serialized preprocessing pipeline.

### Notifications (`notifications/`)

- `base_notifier.py`: notifier abstraction.
- `email.py`: email notification implementation.
- `supabase_realtime.py`: realtime notification channel.
- `webhooks.py`: webhook dispatch support.

### Operational Scripts (`scripts/`)

- `db_migrations.py`: database migration utilities.
- `model_sync.sh`: model artifact sync script.
- `preprocess_cicids2018.py`: parquet-to-model-ready CSV processing for CSE-CIC-IDS2018 data.
- `seed_data.py`: seed/test data generation.
- `user_cleanup.py`: maintenance cleanup tasks.

### Documentation (`docs/`)

- `api.md`: API usage and endpoint documentation.
- `setup.md`: setup and environment instructions.
- `troubleshooting.md`: common issue diagnosis and fixes.

### Infrastructure (`infrastructure/`)

- `k8s/`
	- `configmap.yaml`, `secrets.yaml`, `network-policies.yaml`
	- `api/deployment.yaml`: API deployment + Service.
	- `celery/deployment.yaml`
	- `ingress/ingress.yaml`
	- `redis/deployment.yaml`: Redis deployment + Service.
- `terraform/`
	- `backend.tf`, `main.tf`, `variables.tf`

### CI/CD

- `.github/dependabot.yml`: dependency update automation.
- `.github/workflows/ci.yml`: CI workflow.
- `.github/workflows/cd.yml`: CD workflow.

### Tests (`tests/`)

- `conftest.py`: pytest config + deterministic test environment defaults.
- `integration/test_predict.py`: predict endpoint integration test.
- `unit/test_model_manager.py`: model asset loading unit tests.
- `unit/test_preprocessor.py`: preprocessing transformation unit tests.
- `test_helpers/mocks.py`: reusable mocks/stubs.

## Current Health Check

Test status after fixes:

- `pytest tests -q` -> `3 passed`.

## Runtime Behavior

- `POST /predict/{api_key}` now requires authenticated token context and enforces token/api_key match.
- Prediction response includes:
	- `anomaly`
	- `score`
	- `recommended_action` (`allow`/`monitor`/`throttle`/`block`)
- On anomaly, webhook alerting is attempted as best-effort.
- Action handling is pluggable via `core.security.action_executor` for host app integration.

## Data + Training Flow

1. Put CSE-CIC-IDS2018 parquet files in `final/data/`.
2. Process dataset:
	- `python scripts/preprocess_cicids2018.py`
3. Train model:
	- `python -m ml.training.train --data-path data/processed/csecicids2018_model_ready.csv --epochs 5 --batch-size 4096 --max-rows 0`
4. Outputs are written to `final/model_storage/`.

## AWS Deployment Path (Current)

1. Build and push image to ECR:
	- `docker build -t smkpie-runtime:latest .`
	- `docker tag smkpie-runtime:latest 371601828313.dkr.ecr.ap-south-1.amazonaws.com/smkpie-runtime:latest`
	- `docker push 371601828313.dkr.ecr.ap-south-1.amazonaws.com/smkpie-runtime:latest`
2. K8s manifests already reference the ECR image URI in API/Celery deployments.
3. Apply manifests to your EKS context when available.

## Quick Start (Local)

Run from the `final` folder.

```powershell
# 1) Create/activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install -r requirements.txt

# 3) Start Redis + API + worker
docker compose up -d redis
uvicorn main:app --host 0.0.0.0 --port 8000
```

Optional smoke checks:

```powershell
pytest tests -q
curl http://localhost:8000/health
```

## Quick Start (AWS/EKS)

Run from the `final` folder.

```powershell
# 1) Build image
docker build -t smkpie-runtime:latest .

# 2) Login to ECR
aws ecr get-login-password --region ap-south-1 |
	docker login --username AWS --password-stdin 371601828313.dkr.ecr.ap-south-1.amazonaws.com

# 3) Tag + push
docker tag smkpie-runtime:latest 371601828313.dkr.ecr.ap-south-1.amazonaws.com/smkpie-runtime:latest
docker push 371601828313.dkr.ecr.ap-south-1.amazonaws.com/smkpie-runtime:latest

# 4) Point kubectl to EKS cluster
aws eks update-kubeconfig --region ap-south-1 --name cyber-api-cluster

# 5) Deploy manifests
kubectl apply -f infrastructure/k8s/configmap.yaml
kubectl apply -f infrastructure/k8s/secrets.yaml
kubectl apply -f infrastructure/k8s/network-policies.yaml
kubectl apply -f infrastructure/k8s/redis/deployment.yaml
kubectl apply -f infrastructure/k8s/api/deployment.yaml
kubectl apply -f infrastructure/k8s/celery/deployment.yaml
kubectl apply -f infrastructure/k8s/ingress/ingress.yaml

# 6) Verify rollout
kubectl get pods -o wide
kubectl get svc
kubectl get ingress
```

## Notes

- Supabase and Prometheus imports are handled lazily in critical paths so app startup is resilient when optional packages/features are not enabled.

