from pydantic import BaseModel
from typing import Optional


class TicketResponse(BaseModel):
    id: int
    category_id: int
    creator_id: int
    is_open: bool
    reason: Optional[str]

    class Config:
        orm_mode = True


class TicketUpdate(BaseModel):
    reason: Optional[str]
    category_id: Optional[int]
