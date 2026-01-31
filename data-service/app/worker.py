from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "data-worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_track_started=True,
    imports=["app.tasks"],
    beat_schedule={
        "sync-github-data-every-5-minutes": {
            "task": "app.tasks.sync_all_github_data",
            "schedule": crontab(minute="*/5"),
        },
    },
)
