from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from common.database import Category
from .models.categories import CategoryIn, CategoryResponse, CategoryUpdate
from ..utils.database import get_db

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    statement = select(Category)
    result = await db.execute(statement)
    return result.scalars().all()


@router.post("/", response_model=CategoryResponse)
async def create(category: CategoryIn, db: AsyncSession = Depends(get_db)):
    try:
        # Extract the fields
        c = Category(**category.dict())

        # Add it to the database
        db.add(c)
        await db.commit()

        return c
    except IntegrityError:
        raise HTTPException(status_code=409, detail="field 'name' must be unique")


@router.put("/{primary_key}", response_model=CategoryResponse)
async def update(
    primary_key: int, fields: CategoryUpdate, db: AsyncSession = Depends(get_db)
):
    # Find the response
    category = await db.get(Category, primary_key)
    if category is None:
        raise HTTPException(status_code=404, detail="not found")

    # Set the fields
    if fields.name is not None:
        category.name = fields.name

    # Commit the changes
    try:
        db.add(category)
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="field 'name' must be unique")

    return category


@router.delete("/{primary_key}")
async def delete(primary_key: int, db: AsyncSession = Depends(get_db)):
    # Get the response
    category = await db.get(Category, primary_key)

    # Delete it if it doesn't exist
    if category is not None:
        await db.delete(category)
        await db.commit()

    return {"success": True}
