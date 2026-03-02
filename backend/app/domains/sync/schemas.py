import uuid
from datetime import datetime
from typing import Any
from sqlmodel import SQLModel
from app.domains.sync.enums import ResourceType, SyncStatus

class SyncRecordRead(SQLModel):
    id: uuid.UUID
    location_id: uuid.UUID | None = None
    restaurant_id: uuid.UUID
    resource_type: ResourceType
    status: SyncStatus
    triggered_by: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    items_synced: int
    items_failed: int
    error_log: list[dict[str, Any]]
    celery_task_id: str | None = None
    created_at: datetime
