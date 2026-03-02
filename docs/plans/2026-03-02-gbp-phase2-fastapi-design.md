# GBP Phase 2 Design — Posts, Sync, QA Cleanup, Completion Score (FastAPI Rewrite)

**Date:** 2026-03-02
**Module:** `omnilocal/backend/app/domains/`
**Status:** Approved

---

## 1. Context & Architecture Shift

The project has transitioned from a Django/DRF architecture to the **Full Stack FastAPI Template** (FastAPI, SQLModel, Pydantic, PostgreSQL). This document adapts the original Phase 2 design (Posts, Sync, QA, Completion Score) to the new tech stack.

### Key Architectural Decisions:
1.  **Domain-Driven Design (DDD):** Instead of the flat `app/models.py` and `app/api/routes` structure from the template, we will group features by domain (e.g., `app/domains/posts/`, `app/domains/businesses/`).
2.  **Asynchronous Google API:** Instead of the synchronous `googleapiclient`, we will use `aiogoogle` to make non-blocking, async calls to the Google My Business REST APIs.
3.  **Background Tasks:** We will add **Celery** (with Redis) to the FastAPI docker-compose stack to handle long-running background sync jobs.
4.  **Hard Deletes:** The concept of soft deletion (`SafeDeleteModel`) is dropped for this phase. Standard hard deletes via SQLModel/SQLAlchemy will be used.

---

## 2. Track 1: Posts Module

### 2.1 File Structure

```text
backend/app/domains/posts/
├── __init__.py
├── models.py        # SQLModel table definitions
├── schemas.py       # Pydantic schemas (Create, Read, Update)
├── enums.py         # TopicType, PostState, ActionType, AlertType
├── router.py        # FastAPI APIRouter
├── services.py      # Business logic & Google API integration (aiogoogle)
└── tasks.py         # Celery tasks
```

### 2.2 Domain Model (`models.py`)

```python
import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, String, DateTime
from app.domains.posts.enums import TopicType, PostState, ActionType, AlertType

class LocalPost(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    location_id: uuid.UUID = Field(foreign_key="location.id", index=True)
    
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
    
    media_id: uuid.UUID | None = Field(default=None, foreign_key="mediaitem.id")
    
    # Google-side timestamps
    create_time: datetime | None = Field(default=None)
    update_time: datetime | None = Field(default=None)
    
    # Internal tracking
    last_synced_at: datetime | None = Field(default=None)
    created_by_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2.3 API Routes (`router.py`)

Registered under `/api/v1/posts/`:
*   `GET /posts/` (query params: `location_id`, `topic_type`, `state`)
*   `POST /posts/`
*   `GET /posts/{id}`
*   `PATCH /posts/{id}`
*   `DELETE /posts/{id}`
*   `POST /posts/{id}/sync`

### 2.4 Services (`services.py`)

*   **`PostService`**: Asynchronous class for CRUD operations. Utilizes `aiogoogle` to push creations, updates, and deletions to the GBP API before committing the transaction locally.
*   **`PostSyncService`**: Asynchronously pulls paginated post lists from GBP and reconciles the local DB (upserting new/changed posts, hard-deleting orphans).

### 2.5 Background Tasks (`tasks.py`)

*   `sync_location_posts(location_id: UUID)`: Celery task to trigger the `PostSyncService` for a given location.
*   `periodic_sync_posts()`: Celery Beat task running every 6 hours to dispatch `sync_location_posts` for all active locations.

---

## 3. Track 2: Sync Infrastructure

### 3.1 Model (`backend/app/domains/sync/models.py`)

```python
class SyncRecord(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    location_id: uuid.UUID | None = Field(default=None, foreign_key="location.id", index=True)
    restaurant_id: uuid.UUID = Field(foreign_key="restaurant.id", index=True)
    
    resource_type: ResourceType # Enum: reviews, posts, locations, qa
    status: SyncStatus          # Enum: pending, running, success, partial, failed
    triggered_by: str           # "celery_beat", "user:{uuid}"
    
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    items_synced: int = Field(default=0)
    items_failed: int = Field(default=0)
    
    # Store errors as JSON
    error_log: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    celery_task_id: str | None = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.2 Celery Integration

A utility function or base class will be provided to standardise wrapping Celery tasks with `SyncRecord` creation and status updates (Running -> Success/Failed).

### 3.3 API (`backend/app/domains/sync/router.py`)

Read-only API for the frontend dashboard:
*   `GET /sync/records/`
*   `GET /sync/records/{id}`

---

## 4. Track 3: QA Module Cleanup

*   **Structure:** Create `app/domains/qa/`.
*   **Soft Delete:** Dropped.
*   **API Client:** Refactor existing QA interactions to use `aiogoogle`.
*   **Rate Limiting:** Implement `asyncio.sleep()` based rate-limiting in the `aiogoogle` loop to handle Google's strict Q&A quota.

---

## 5. Track 4: Profile Completion Score

### 5.1 Model (`backend/app/domains/businesses/models.py`)

```python
class ProfileCompletionScore(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    location_id: uuid.UUID = Field(foreign_key="location.id", unique=True)
    
    total_points: int = Field(default=15)
    achieved_points: int = Field(default=0)
    completion_pct: float = Field(default=0.0)
    
    missing_criteria: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    completed_criteria: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    last_calculated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 5.2 Calculator Service

*   `ProfileCompletionCalculator`: A synchronous or async service that reads the local DB only (no Google API calls) to evaluate the 15 completion criteria.

### 5.3 Triggering Calculations

Instead of Django's `post_save` signals, we will explicitly trigger a background Celery task (`recalculate_completion_score.delay(location_id)`) inside the FastAPI service layers whenever a `Location`, `MediaItem`, `Question`, or `LocalPost` is mutated.

### 5.4 API

Appended to the Businesses/Locations router:
*   `GET /locations/{id}/completion-score` (Calculates on the fly if a score doesn't exist).