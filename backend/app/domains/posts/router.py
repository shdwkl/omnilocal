import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.api.deps import get_db
from app.domains.posts.models import LocalPost
from app.domains.posts.schemas import LocalPostCreate, LocalPostUpdate, LocalPostRead
from app.domains.posts.services import PostService

router = APIRouter()

@router.get("/", response_model=list[LocalPostRead])
async def read_posts(location_id: uuid.UUID, skip: int = 0, limit: int = 100, session: Session = Depends(get_db)) -> Any:
    service = PostService(session)
    return await service.get_posts(location_id, skip=skip, limit=limit)

@router.post("/", response_model=LocalPostRead)
async def create_post(post_in: LocalPostCreate, session: Session = Depends(get_db)) -> Any:
    service = PostService(session)
    return await service.create_post(post_in)

@router.get("/{id}", response_model=LocalPostRead)
async def read_post(id: uuid.UUID, session: Session = Depends(get_db)) -> Any:
    service = PostService(session)
    post = await service.get_post(id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.patch("/{id}", response_model=LocalPostRead)
async def update_post(id: uuid.UUID, post_in: LocalPostUpdate, session: Session = Depends(get_db)) -> Any:
    service = PostService(session)
    post = await service.update_post(id, post_in)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.delete("/{id}")
async def delete_post(id: uuid.UUID, session: Session = Depends(get_db)) -> Any:
    service = PostService(session)
    success = await service.delete_post(id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}

@router.post("/{id}/sync")
async def sync_post(id: uuid.UUID, session: Session = Depends(get_db)) -> Any:
    service = PostService(session)
    post = await service.get_post(id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    # TODO: Fetch specific post from GBP and update
    return post
