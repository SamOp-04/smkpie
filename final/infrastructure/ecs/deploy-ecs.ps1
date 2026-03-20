param(
    [string]$Region = "ap-south-1",
    [string]$Cluster = "smkpie-cluster",
    [string]$ApiService = "smkpie-api-svc",
    [string]$WorkerService = "smkpie-celery-worker-svc",
    [string]$BeatService = "smkpie-celery-beat-svc"
)

$ErrorActionPreference = "Stop"

Write-Host "Registering task definitions..."
aws ecs register-task-definition --region $Region --cli-input-json file://infrastructure/ecs/taskdef-api.json | Out-Null
aws ecs register-task-definition --region $Region --cli-input-json file://infrastructure/ecs/taskdef-celery-worker.json | Out-Null
aws ecs register-task-definition --region $Region --cli-input-json file://infrastructure/ecs/taskdef-celery-beat.json | Out-Null

Write-Host "Forcing ECS service deployments..."
aws ecs update-service --region $Region --cluster $Cluster --service $ApiService --force-new-deployment | Out-Null
aws ecs update-service --region $Region --cluster $Cluster --service $WorkerService --force-new-deployment | Out-Null
aws ecs update-service --region $Region --cluster $Cluster --service $BeatService --force-new-deployment | Out-Null

Write-Host "Waiting for services to become stable..."
aws ecs wait services-stable --region $Region --cluster $Cluster --services $ApiService $WorkerService $BeatService

Write-Host "ECS deployment completed successfully."
