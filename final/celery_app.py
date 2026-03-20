from celery import Celery
from celery.schedules import crontab
from core.config import settings

celery = Celery(
    __name__,
    broker=f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/1",
    include=["tasks"]
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_expires=3600,
    worker_prefetch_multiplier=4
)

# Schedule periodic tasks with Celery Beat
celery.conf.beat_schedule = {
    'check-model-performance-daily': {
        'task': 'tasks.check_model_performance',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    'evaluate-retraining-weekly': {
        'task': 'tasks.evaluate_retraining_need',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Run Sunday at 3 AM
    },
}