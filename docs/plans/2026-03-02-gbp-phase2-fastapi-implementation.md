# GBP Phase 2 (FastAPI) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the GBP Phase 2 features (Posts, Sync, QA, Completion Score) using FastAPI, SQLModel, and a Domain-Driven Design (DDD) structure.

**Architecture:** We are transitioning to DDD for new features (`app/domains/`), leaving the existing template (`User`, `Item`) as is for now. We will introduce Celery+Redis for background jobs and `aiogoogle` for asynchronous Google API interactions. Hard deletes will be used.

**Tech Stack:** FastAPI, SQLModel, Pydantic, PostgreSQL, Celery, Redis, `aiogoogle`.

---

### Task 1: Setup Infrastructure & Dependencies

**Files:**
- Modify: `compose.yml`
- Modify: `backend/pyproject.toml` or `backend/requirements.txt` / `uv.lock`
- Create: `backend/app/celery_app.py`
- Modify: `backend/app/api/main.py`

**Step 1: Add dependencies**
Install `celery`, `redis`, and `aiogoogle`. If using `uv`, run `uv add celery redis aiogoogle` in the `backend/` directory. Wait for completion.

**Step 2: Add Redis to `compose.yml`**
Add a `redis` service to `compose.yml` to act as the Celery broker. Add a `celeryworker` service using the backend image.

**Step 3: Initialize Celery App**
Create `backend/app/celery_app.py`:
```python
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=str(settings.REDIS_URI) if hasattr(settings, "REDIS_URI") else "redis://redis:6379/0"
)
celery_app.conf.task_routes = {"app.domains.*.tasks.*": "main-queue"}
```
Ensure `REDIS_URI` is added to `backend/app/core/config.py`.

**Step 4: Commit**
```bash
git add compose.yml backend/pyproject.toml backend/uv.lock backend/app/celery_app.py backend/app/core/config.py
git commit -m "chore: add celery, redis, and aiogoogle dependencies"
```

---

### Task 2: Implement Track 2 - Sync Infrastructure

**Files:**
- Create: `backend/app/domains/sync/__init__.py`
- Create: `backend/app/domains/sync/enums.py`
- Create: `backend/app/domains/sync/models.py`
- Create: `backend/app/domains/sync/schemas.py`
- Create: `backend/app/domains/sync/router.py`
- Modify: `backend/app/api/main.py`

**Step 1: Create Enums**
Create `backend/app/domains/sync/enums.py`:
```python
from enum import Enum

class ResourceType(str, Enum):
    REVIEWS = "reviews"
    POSTS = "posts"
    LOCATIONS = "locations"
    MEDIA = "media"
    QA = "qa"
    PERFORMANCE = "performance"

class SyncStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
```

**Step 2: Create SQLModel**
Create `backend/app/domains/sync/models.py`:
```python
import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON
from app.domains.sync.enums import ResourceType, SyncStatus

class SyncRecord(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # Note: Using UUID placeholders until Location/Restaurant models exist
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
```

**Step 3: Create Schemas & Router**
Create `schemas.py` (Read schemas for SyncRecord). Create `router.py` with `GET /sync/records/`.

**Step 4: Register Router & Make Migrations**
Include the router in `backend/app/api/main.py` (`api_router.include_router(sync_router, prefix="/sync", tags=["sync"])`).
Ensure models are imported in `backend/app/alembic/env.py`.
Run Alembic: `cd backend && alembic revision --autogenerate -m "Add SyncRecord model"`

**Step 5: Commit**
```bash
git add backend/app/domains/sync/ backend/app/api/main.py backend/app/alembic/
git commit -m "feat(sync): add SyncRecord model and read-only API"
```

---

### Task 3: Implement Track 1 - Posts Module (Models & Setup)

**Files:**
- Create: `backend/app/domains/posts/__init__.py`
- Create: `backend/app/domains/posts/enums.py`
- Create: `backend/app/domains/posts/models.py`
- Create: `backend/app/domains/posts/schemas.py`

**Step 1: Create Enums**
Create `enums.py` with `TopicType`, `PostState`, `ActionType`, `AlertType` as per the design doc.

**Step 2: Create Model**
Create `models.py` for `LocalPost` using SQLModel, mapping exactly to the design doc. Use `uuid.UUID` for foreign keys (`location_id`, `media_id`, `created_by_id`).

**Step 3: Create Schemas**
Create `schemas.py` with `LocalPostCreate`, `LocalPostUpdate`, and `LocalPostRead` Pydantic models.

**Step 4: Make Migrations**
Ensure `LocalPost` is imported in `alembic/env.py`.
Run: `cd backend && alembic revision --autogenerate -m "Add LocalPost model"`

**Step 5: Commit**
```bash
git add backend/app/domains/posts/ backend/app/alembic/
git commit -m "feat(posts): add LocalPost model and schemas"
```

---

### Task 4: Implement Track 1 - Posts Module (Services & API)

**Files:**
- Create: `backend/app/domains/posts/services.py`
- Create: `backend/app/domains/posts/router.py`
- Modify: `backend/app/api/main.py`

**Step 1: PostService Stub**
Create `services.py` with a basic async `PostService` class handling local DB CRUD (create, read, list, update, delete). Add placeholder methods for `aiogoogle` integration (`_push_to_google`, etc.).

**Step 2: Post Router**
Create `router.py` with REST endpoints for `/posts/` utilizing `PostService` and standard FastAPI dependency injection (`Session`).

**Step 3: Register Router**
Include the router in `backend/app/api/main.py` (`prefix="/posts"`).

**Step 4: Commit**
```bash
git add backend/app/domains/posts/services.py backend/app/domains/posts/router.py backend/app/api/main.py
git commit -m "feat(posts): add CRUD services and REST endpoints for LocalPosts"
```

---

### Task 5: Implement Track 1 - Posts Module (Celery Tasks)

**Files:**
- Create: `backend/app/domains/posts/tasks.py`

**Step 1: Background Sync Tasks**
Create `tasks.py`:
```python
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
```

**Step 2: Commit**
```bash
git add backend/app/domains/posts/tasks.py
git commit -m "feat(posts): add background sync tasks stubs"
```

---

### Task 6: Implement Track 4 - Profile Completion Score

**Files:**
- Create: `backend/app/domains/businesses/__init__.py`
- Create: `backend/app/domains/businesses/models.py`
- Create: `backend/app/domains/businesses/schemas.py`
- Create: `backend/app/domains/businesses/services.py`
- Create: `backend/app/domains/businesses/router.py`
- Modify: `backend/app/api/main.py`

**Step 1: Create Model**
Create `backend/app/domains/businesses/models.py` with `ProfileCompletionScore` containing the 15 point criteria and JSON lists for missing/completed criteria.

**Step 2: Create Calculator Service**
Create `services.py` with `ProfileCompletionCalculator` class containing the evaluation logic for the 15 criteria (stubbed methods returning booleans for now).

**Step 3: Create API**
Create `router.py` with `GET /locations/{id}/completion-score`.
Include it in `backend/app/api/main.py`.

**Step 4: Migrations**
Run: `cd backend && alembic revision --autogenerate -m "Add ProfileCompletionScore model"`

**Step 5: Commit**
```bash
git add backend/app/domains/businesses/ backend/app/api/main.py backend/app/alembic/
git commit -m "feat(businesses): add profile completion score models and calculator"
```

---

### Task 7: Track 3 - QA Module Stub Setup

**Files:**
- Create: `backend/app/domains/qa/__init__.py`
- Create: `backend/app/domains/qa/models.py`
- Create: `backend/app/domains/qa/services.py`

**Step 1: Scaffold QA**
Since QA is just a cleanup and we dropped soft-delete, just create the domain folders and a stub `services.py` demonstrating where the `aiogoogle` rate-limiting wrapper will go (e.g., `await asyncio.sleep(1.0)` between paginated requests).

**Step 2: Commit**
```bash
git add backend/app/domains/qa/
git commit -m "chore(qa): setup qa domain folder and rate-limit stubs"
```