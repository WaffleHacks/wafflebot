from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AnnouncementIn(BaseModel):
    send_at: datetime
    content: str
    embed: bool = False
    title: Optional[str] = None


class Announcement(BaseModel):
    id: int
    send_at: datetime
    content: str
    embed: bool
    title: Optional[str]

    class Config:
        orm_mode = True


class AnnouncementUpdate(BaseModel):
    send_at: Optional[datetime]
    content: Optional[str]
    embed: Optional[bool]
    title: Optional[str]
