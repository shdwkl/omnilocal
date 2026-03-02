import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

class ProfileCompletionScore(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    location_id: uuid.UUID = Field(unique=True, index=True)
    
    total_points: int = Field(default=15)
    achieved_points: int = Field(default=0)
    completion_pct: float = Field(default=0.0)
    
    missing_criteria: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    completed_criteria: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    last_calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
