# SMKpie

SMKpie is a FastAPI-based cybersecurity anomaly-detection platform with:

- API endpoints for auth, prediction, health, logs, and settings.
- ML serving and monitoring components.
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

- `Dockerfile`: container image build for the API.
- `docker-compose.yml`: local multi-service orchestration.
- `requirements.txt`: Python dependencies for the app.

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
	- `model_manager.py`: model/preprocessor asset loading and saving.
	- `predictor.py`: prediction + anomaly threshold logic.
	- `preprocessor.py`: feature preprocessing and scaler persistence.
- `training/`
	- `hyperparams.yaml`: training hyperparameters.
	- `train.py`: model training pipeline.
- `versioning/`
	- `model_version.py`: model version metadata/management.

### Model Artifacts (`model_storage/`)

- `model.keras`: serialized trained model.
- `preprocessor.joblib`: serialized preprocessing pipeline.

### Notifications (`notifications/`)

- `base_notifier.py`: notifier abstraction.
- `email.py`: email notification implementation.
- `supabase_realtime.py`: realtime notification channel.
- `webhooks.py`: webhook dispatch support.

### Operational Scripts (`scripts/`)

- `db_migrations.py`: database migration utilities.
- `model_sync.sh`: model artifact sync script.
- `seed_data.py`: seed/test data generation.
- `user_cleanup.py`: maintenance cleanup tasks.

### Documentation (`docs/`)

- `api.md`: API usage and endpoint documentation.
- `setup.md`: setup and environment instructions.
- `troubleshooting.md`: common issue diagnosis and fixes.

### Infrastructure (`infrastructure/`)

- `k8s/`
	- `configmap.yaml`, `secrets.yaml`, `network-policies.yaml`
	- `api/deployment.yaml`: API deployment definition.
	- `celery/deployment.yaml`, `celery/worker-autoscaling.yaml`
	- `ingress/ingress.yaml`, `ingress/tls.yaml`
	- `monitoring/prometheus.yaml`
	- `redis/deployment.yaml`
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

## Notes

- Some production dependencies (notably TensorFlow/Supabase combinations) are version-sensitive across Python versions; tests have been stabilized to run without external service dependencies.

