# ECS Service Bootstrap (Fargate)

This guide creates three ECS services:
- `smkpie-api-svc` (behind ALB target group)
- `smkpie-celery-worker-svc`
- `smkpie-celery-beat-svc`

## 1) Prerequisites

- ECS cluster exists: `smkpie-cluster`
- VPC private subnets for tasks: `<SUBNET_A>`, `<SUBNET_B>`
- Security group for ECS tasks: `<ECS_TASK_SG>`
- Application Load Balancer target group for API port 8000: `<API_TARGET_GROUP_ARN>`

## 2) Register task definitions

```bash
aws ecs register-task-definition --region ap-south-1 --cli-input-json file://infrastructure/ecs/taskdef-api.json
aws ecs register-task-definition --region ap-south-1 --cli-input-json file://infrastructure/ecs/taskdef-celery-worker.json
aws ecs register-task-definition --region ap-south-1 --cli-input-json file://infrastructure/ecs/taskdef-celery-beat.json
```

## 3) Create API service

```bash
aws ecs create-service \
  --region ap-south-1 \
  --cluster smkpie-cluster \
  --service-name smkpie-api-svc \
  --task-definition smkpie-api \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_A>,<SUBNET_B>],securityGroups=[<ECS_TASK_SG>],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=<API_TARGET_GROUP_ARN>,containerName=api,containerPort=8000"
```

## 4) Create Celery services

```bash
aws ecs create-service \
  --region ap-south-1 \
  --cluster smkpie-cluster \
  --service-name smkpie-celery-worker-svc \
  --task-definition smkpie-celery-worker \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_A>,<SUBNET_B>],securityGroups=[<ECS_TASK_SG>],assignPublicIp=DISABLED}"

aws ecs create-service \
  --region ap-south-1 \
  --cluster smkpie-cluster \
  --service-name smkpie-celery-beat-svc \
  --task-definition smkpie-celery-beat \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_A>,<SUBNET_B>],securityGroups=[<ECS_TASK_SG>],assignPublicIp=DISABLED}"
```

## 5) Verify

```bash
aws ecs describe-services --region ap-south-1 --cluster smkpie-cluster \
  --services smkpie-api-svc smkpie-celery-worker-svc smkpie-celery-beat-svc \
  --query "services[].{name:serviceName,status:status,desired:desiredCount,running:runningCount}"
```

## 6) Rolling update after a new image push

```bash
powershell -ExecutionPolicy Bypass -File infrastructure/ecs/deploy-ecs.ps1 \
  -Region ap-south-1 \
  -Cluster smkpie-cluster \
  -ApiService smkpie-api-svc \
  -WorkerService smkpie-celery-worker-svc \
  -BeatService smkpie-celery-beat-svc
```
