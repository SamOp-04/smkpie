from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.utils import setup_logging
from core.database.redis_manager import redis_manager
from core.middleware.action_enforcement import ActionEnforcementMiddleware
from core.security.action_executor import set_action_executor, RedisActionExecutor
from ml.serving.model_manager import ModelManager
from api.routes import auth, predict, health, settings, logs, admin, model_metrics
import logging

app = FastAPI()

# Setup
setup_logging()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add action enforcement middleware to check for blocked/throttled API keys
app.add_middleware(ActionEnforcementMiddleware)

# Routes
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(health.router)
app.include_router(settings.router)
app.include_router(logs.router)
app.include_router(admin.router)
app.include_router(model_metrics.router)

# Root Route
@app.get("/")
async def root():
    return {"message": "🚀 Welcome to SMKpie!"}

@app.on_event("startup")
async def startup():
    # Initialize async Redis
    try:
        await redis_manager.initialize()
        redis = await redis_manager.get_connection()
        await redis.ping()
        logging.info("✓ Redis connection OK")
    except Exception as e:
        logging.error(f"✗ Redis connection failed: {e}")

    # Set action executor to Redis-based enforcement
    set_action_executor(RedisActionExecutor())
    logging.info("✓ RedisActionExecutor enabled")

    # Preload model assets
    try:
        model_manager = ModelManager()
        model_manager.load_assets()
        logging.info("✓ Model assets preloaded successfully")
    except FileNotFoundError as e:
        logging.error(f"✗ Model assets not found: {e}")
        logging.error("Run training script to generate model files")
    except Exception as e:
        logging.error(f"✗ Failed to preload model: {e}")

    print("🚀 Welcome to SMKpie!")

@app.on_event("shutdown")
async def shutdown():
    await redis_manager.close()
    logging.info("Shutdown complete")
