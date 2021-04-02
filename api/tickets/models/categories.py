from pydantic import BaseModel
from typing import Optional


class CategoryIn(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CategoryUpdate(BaseModel):
    name: Optional[str]
