from typing import Optional

from .base import Model, find_primary_key
from ..tables import messages


class Message(Model):
    __table__ = messages
    __primary_key__ = find_primary_key(messages)

    id: Optional[int]
    ticket_id: int
    sender_id: int
    is_reaction: bool
    content: str
