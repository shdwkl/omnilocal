import uuid
from datetime import datetime
from sqlmodel import SQLModel
from app.domains.posts.enums import TopicType, PostState, ActionType, AlertType

class LocalPostBase(SQLModel):
    location_id: uuid.UUID
    topic_type: TopicType = TopicType.STANDARD
    language_code: str = "en"
    summary: str | None = None
    alert_type: AlertType | None = None
    event_title: str | None = None
    event_start_time: datetime | None = None
    event_end_time: datetime | None = None
    offer_coupon: str | None = None
    offer_redeem_url: str | None = None
    offer_terms: str | None = None
    cta_action_type: ActionType | None = None
    cta_url: str | None = None
    media_id: uuid.UUID | None = None

class LocalPostCreate(LocalPostBase):
    pass

class LocalPostUpdate(LocalPostBase):
    pass

class LocalPostRead(LocalPostBase):
    id: uuid.UUID
    google_post_name: str
    state: PostState
    create_time: datetime | None = None
    update_time: datetime | None = None
    last_synced_at: datetime | None = None
    created_by_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
