from app.celery_app import celery_app
import uuid

@celery_app.task
def sync_location_posts(location_id: uuid.UUID):
    # Stub: Initialize PostSyncService and sync
    pass

@celery_app.task
def periodic_sync_posts():
    # Stub: Dispatch sync_location_posts for all active locations
    pass
