from pydantic import BaseModel
from typing import Dict, Optional


class CannedResponseIn(BaseModel):
    key: str
    title: str
    content: str
    fields: Dict[str, str]


class CannedResponse(BaseModel):
    id: int
    key: str
    title: str
    content: str
    fields: Dict[str, str]

    class Config:
        orm_mode = True


class CannedResponseUpdate(BaseModel):
    key: Optional[str]
    title: Optional[str]
    content: Optional[str]
    fields: Optional[Dict[str, str]]
