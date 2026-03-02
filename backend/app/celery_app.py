from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=str(settings.REDIS_URI) if hasattr(settings, "REDIS_URI") else "redis://redis:6379/0"
)
celery_app.conf.task_routes = {"app.domains.*.tasks.*": "main-queue"}
