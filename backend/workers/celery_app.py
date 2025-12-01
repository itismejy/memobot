"""Celery application for background tasks."""
from celery import Celery
from backend.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "memobot",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["backend.workers.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    "summarize-sessions-every-hour": {
        "task": "backend.workers.tasks.summarize_sessions_task",
        "schedule": 3600.0,  # Every hour
    },
    "update-profiles-daily": {
        "task": "backend.workers.tasks.update_profiles_task",
        "schedule": 86400.0,  # Every day
    },
}

