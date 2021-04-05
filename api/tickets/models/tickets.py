from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TicketResponse(BaseModel):
    id: int
    category_id: Optional[int]
    creator_id: int
    is_open: bool
    reason: Optional[str]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class TicketUpdate(BaseModel):
    reason: Optional[str]
    category_id: Optional[int]


class MessageSender(BaseModel):
    id: int
    username: str
    avatar: str

    class Config:
        orm_mode = True


class TicketMessage(BaseModel):
    id: int
    sender: MessageSender
    created_at: Optional[datetime]
    content: str

    class Config:
        orm_mode = True
