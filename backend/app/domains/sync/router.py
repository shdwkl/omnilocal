from fastapi import APIRouter
from app.domains.sync.schemas import SyncRecordRead

router = APIRouter()

# TODO: Add dependencies for auth/db session once services are built
@router.get("/", response_model=list[SyncRecordRead])
def read_sync_records() -> list[SyncRecordRead]:
    # Placeholder for list endpoint
    return []

@router.get("/{id}", response_model=SyncRecordRead)
def read_sync_record(id: str) -> SyncRecordRead:
    # Placeholder for retrieve endpoint
    pass
