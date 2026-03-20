import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))


TEST_ENV_DEFAULTS = {
	"SUPABASE_URL": "https://example.supabase.co",
	"SUPABASE_KEY": "test-key",
	"SUPABASE_SERVICE_ROLE_KEY": "test-service-role",
	"SUPABASE_JWT_SECRET": "test-jwt-secret",
	"AWS_ACCESS_KEY_ID": "test-access-key",
	"AWS_SECRET_ACCESS_KEY": "test-secret-key",
	"AWS_REGION": "us-east-1",
	"S3_BUCKET": "test-bucket",
	"MODEL_UPDATE_INTERVAL": "60",
	"ANOMALY_THRESHOLD": "0.5",
	"MAX_REQUESTS_PER_MINUTE": "120",
	"EMAIL_SENDER": "noreply@example.com",
	"SMTP_HOST": "localhost",
	"SMTP_PORT": "1025",
	"SMTP_USER": "test-user",
	"SMTP_PASSWORD": "test-password",
}

for env_key, env_value in TEST_ENV_DEFAULTS.items():
	os.environ.setdefault(env_key, env_value)
