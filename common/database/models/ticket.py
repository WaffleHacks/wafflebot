from pydantic import validator
from typing import Optional

from .base import Model, find_primary_key
from ..tables import tickets


class Ticket(Model):
    __table__ = tickets
    __primary_key__ = find_primary_key(tickets)

    id: Optional[int]
    category_id: int
    sender_id: int
    is_open: bool
    reason: str

    @validator("reason")
    def reason_less_than_256_characters(cls, v):
        if len(v) > 256:
            raise ValueError("reason must be less than 256 characters")
        return v
