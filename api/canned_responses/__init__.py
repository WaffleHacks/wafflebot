from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from common.database import CannedResponse
from .models import (
    CannedResponse as CannedResponseModel,
    CannedResponseIn,
    CannedResponseUpdate,
)
from ..utils.database import get_db

router = APIRouter()


@router.get("/", response_model=List[CannedResponseModel])
async def list_responses(db: AsyncSession = Depends(get_db)):
    statement = select(CannedResponse)
    result = await db.execute(statement)
    responses = result.scalars().all()
    return responses


@router.post("/")
async def create(response: CannedResponseIn, db: AsyncSession = Depends(get_db)):
    try:
        # Extract the fields
        r = CannedResponse(**response.dict())

        # Add it to the database
        async with db.begin():
            db.add(r)

        return r
    except IntegrityError:
        raise HTTPException(status_code=409, detail="field 'key' must be unique")


@router.put("/{primary_key}", response_model=CannedResponseModel)
async def update(
    primary_key: int, fields: CannedResponseUpdate, db: AsyncSession = Depends(get_db)
):
    # Get the response
    response = await db.get(CannedResponse, primary_key)
    if response is None:
        raise HTTPException(status_code=404, detail="not found")

    # Set fields
    if fields.key is not None:
        response.key = fields.key
    if fields.title is not None:
        response.title = fields.title
    if fields.content is not None:
        response.content = fields.content
    if fields.fields is not None:
        response.fields = fields.fields

    # Commit the changes
    try:
        db.add(response)
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="field 'key' must be unique")

    return response


@router.delete("/{primary_key}")
async def delete(primary_key: int, db: AsyncSession = Depends(get_db)):
    # Get the response
    response = await db.get(CannedResponse, primary_key)

    # Delete it if it exists
    if response is not None:
        await db.delete(response)
        await db.commit()

    return {"success": True}
