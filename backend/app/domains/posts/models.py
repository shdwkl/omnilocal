import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from app.domains.posts.enums import TopicType, PostState, ActionType, AlertType

class LocalPost(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # Using simple UUID indexing until Location model exists
    location_id: uuid.UUID = Field(index=True)
    
    google_post_name: str = Field(max_length=255, unique=True)
    topic_type: TopicType = Field(default=TopicType.STANDARD)
    state: PostState = Field(default=PostState.PROCESSING)
    language_code: str = Field(default="en", max_length=10)
    summary: str | None = Field(default=None)
    alert_type: AlertType | None = Field(default=None)
    
    # Event fields
    event_title: str | None = Field(default=None, max_length=255)
    event_start_time: datetime | None = Field(default=None)
    event_end_time: datetime | None = Field(default=None)
    
    # Offer fields
    offer_coupon: str | None = Field(default=None, max_length=255)
    offer_redeem_url: str | None = Field(default=None)
    offer_terms: str | None = Field(default=None)
    
    # CTA fields
    cta_action_type: ActionType | None = Field(default=None)
    cta_url: str | None = Field(default=None)
    
    media_id: uuid.UUID | None = Field(default=None)
    
    # Google-side timestamps
    create_time: datetime | None = Field(default=None)
    update_time: datetime | None = Field(default=None)
    
    # Internal tracking
    last_synced_at: datetime | None = Field(default=None)
    created_by_id: uuid.UUID | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
