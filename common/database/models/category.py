from pydantic import validator
from typing import Optional

from .base import Model, find_primary_key
from ..tables import categories


class Category(Model):
    __table__ = categories
    __primary_key__ = find_primary_key(categories)

    id: Optional[int]
    name: str

    @validator("name")
    def name_less_than_64_characters(cls, v: str):
        if len(v) > 64:
            raise ValueError("name must be less than 64 characters")
        return v
