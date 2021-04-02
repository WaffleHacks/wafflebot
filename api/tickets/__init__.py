from fastapi import APIRouter, Depends, HTTPException

from .categories import router as categories_router

router = APIRouter()
router.include_router(
    categories_router, prefix="/categories", tags=["tickets", "categories"]
)
