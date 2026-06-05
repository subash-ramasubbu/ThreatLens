from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "threatlens",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"],
)

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "fetch-threats-every-hour": {
        "task": "app.tasks.fetch_all_threats",
        "schedule": crontab(minute=0, hour="*"),
    },
    "run-correlation-every-hour": {
        "task": "app.tasks.run_correlation_task",
        "schedule": crontab(minute=10, hour="*"),
    },
}