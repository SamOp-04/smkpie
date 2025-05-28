from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.utils import setup_logging
from core.database.redis_manager import redis_manager
from api.routes import auth, predict, health, settings, logs

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

# Routes
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(health.router)
app.include_router(settings.router)
app.include_router(logs.router)
# Root Route
@app.get("/")
async def root():
    return {"message": "🚀 Welcome to SMKpie!"}

@app.on_event("startup")
async def startup():
    redis_manager.get_connection().ping()
    print("🚀 Welcome to SMKpie!")

@app.on_event("shutdown")
async def shutdown():
    redis_manager.get_connection().close()
