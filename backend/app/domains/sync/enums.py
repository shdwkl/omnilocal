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
