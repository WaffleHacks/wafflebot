from pydantic import validator
from typing import Optional

from .base import Model, find_primary_key
from ..tables import canned_responses


class CannedResponse(Model):
    __table__ = canned_responses
    __primary_key__ = find_primary_key(canned_responses)

    id: Optional[int]
    key: str
    title: str
    content: str
    fields: str

    @validator("key")
    def key_less_than_32_characters(cls, v: str):
        if len(v) > 32:
            raise ValueError("key must be less than 32 characters")
        return v

    @validator("title")
    def title_less_than_256_characters(cls, v: str):
        if len(v) > 256:
            raise ValueError("title must be less than 256 characters")
        return v
