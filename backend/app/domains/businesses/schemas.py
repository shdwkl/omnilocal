import uuid
from datetime import datetime
from sqlmodel import SQLModel

class ProfileCompletionScoreRead(SQLModel):
    id: uuid.UUID
    location_id: uuid.UUID
    total_points: int
    achieved_points: int
    completion_pct: float
    missing_criteria: list[str]
    completed_criteria: list[str]
    last_calculated_at: datetime
