from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from common.database import get_db, Announcement
from common.observability import with_transaction
from .models import (
    Announcement as AnnouncementModel,
    AnnouncementIn,
    AnnouncementUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[AnnouncementModel])
@with_transaction("announcements.list")
async def list_announcements(db: AsyncSession = Depends(get_db)):
    statement = select(Announcement)
    result = await db.execute(statement)
    announcements = result.scalars().all()
    return announcements


@router.post("/", response_model=AnnouncementModel)
@with_transaction("announcements.create")
async def create(announcement: AnnouncementIn, db: AsyncSession = Depends(get_db)):
    try:
        # Extract the fields
        a = Announcement(**announcement.dict())
        if not a.embed:
            a.title = None

        # Add it to the database
        async with db.begin():
            db.add(a)

        return a
    except IntegrityError:
        raise HTTPException(status_code=400, detail="field 'title' is required")


@router.put("/{primary_key}", response_model=AnnouncementModel)
@with_transaction("announcements.update")
async def update(
    primary_key: int, fields: AnnouncementUpdate, db: AsyncSession = Depends(get_db)
):
    # Get the announcement
    announcement = await db.get(Announcement, primary_key)
    if announcement is None:
        raise HTTPException(status_code=404, detail="not found")

    # Set any fields
    if fields.send_at is not None:
        announcement.send_at = fields.send_at
    if fields.name is not None:
        announcement.name = fields.name
    if fields.content is not None:
        announcement.content = fields.content
    if fields.title is not None:
        announcement.title = fields.title
    if fields.embed is not None:
        announcement.embed = fields.embed
        if not fields.embed:
            announcement.title = None

    # Commit the changes
    try:
        db.add(announcement)
        await db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="field 'title' is required when an embed is requested",
        )

    return announcement


@router.delete("/{primary_key}")
@with_transaction("announcements.delete")
async def delete(primary_key: int, db: AsyncSession = Depends(get_db)):
    # Get the announcement
    announcement = await db.get(Announcement, primary_key)

    # Delete if exists
    if announcement is not None:
        await db.delete(announcement)
        await db.commit()

    return {"success": True}
