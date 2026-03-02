import uuid
from typing import Any
from sqlmodel import Session, select
from app.domains.posts.models import LocalPost
from app.domains.posts.schemas import LocalPostCreate, LocalPostUpdate

class PostService:
    def __init__(self, session: Session):
        self.session = session

    async def get_posts(self, location_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[LocalPost]:
        statement = select(LocalPost).where(LocalPost.location_id == location_id).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    async def get_post(self, id: uuid.UUID) -> LocalPost | None:
        return self.session.get(LocalPost, id)

    async def create_post(self, post_in: LocalPostCreate) -> LocalPost:
        # TODO: aiogoogle call to push to GBP before local save
        db_post = LocalPost.model_validate(post_in)
        # Mock google_post_name for now
        db_post.google_post_name = f"locations/{db_post.location_id}/localPosts/{uuid.uuid4().hex}"
        self.session.add(db_post)
        self.session.commit()
        self.session.refresh(db_post)
        return db_post

    async def update_post(self, id: uuid.UUID, post_in: LocalPostUpdate) -> LocalPost | None:
        db_post = await self.get_post(id)
        if not db_post:
            return None
        # TODO: aiogoogle call to update on GBP
        update_data = post_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_post, key, value)
        self.session.add(db_post)
        self.session.commit()
        self.session.refresh(db_post)
        return db_post

    async def delete_post(self, id: uuid.UUID) -> bool:
        db_post = await self.get_post(id)
        if not db_post:
            return False
        # TODO: aiogoogle call to delete from GBP
        self.session.delete(db_post)
        self.session.commit()
        return True

class PostSyncService:
    def __init__(self, session: Session):
        self.session = session

    async def sync_location_posts(self, location_id: uuid.UUID) -> dict[str, Any]:
        # TODO: aiogoogle to list all posts and reconcile with local DB
        pass
