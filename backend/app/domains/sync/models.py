import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON
from app.domains.sync.enums import ResourceType, SyncStatus

class SyncRecord(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    location_id: uuid.UUID | None = Field(default=None, index=True) 
    restaurant_id: uuid.UUID = Field(index=True)
    
    resource_type: ResourceType
    status: SyncStatus = Field(default=SyncStatus.PENDING)
    triggered_by: str
    
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    items_synced: int = Field(default=0)
    items_failed: int = Field(default=0)
    
    error_log: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    celery_task_id: str | None = Field(default=None)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
