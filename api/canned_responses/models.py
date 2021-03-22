from pydantic import BaseModel
from typing import Dict, Optional


class CannedResponse(BaseModel):
    id: int
    key: str
    title: str
    content: str
    fields: Dict[str, str]


class UpdateCannedResponse(BaseModel):
    key: Optional[str]
    title: Optional[str]
    content: Optional[str]
    fields: Optional[Dict[str, str]]
