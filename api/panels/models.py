from pydantic import BaseModel
from typing import List, Optional


class ReactionIn(BaseModel):
    emoji: str
    category_id: int


class PanelIn(BaseModel):
    title: str
    content: str
    channel_id: int
    reactions: List[ReactionIn]


class GenericPanel(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        orm_mode = True


class Category(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Reaction(BaseModel):
    id: int
    emoji: str
    category: Category

    class Config:
        orm_mode = True


class SpecificPanel(BaseModel):
    id: int
    title: str
    content: str
    channel: str
    reactions: List[Reaction]


class PanelUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    channel_id: Optional[int]


class ReactionUpdate(BaseModel):
    category_id: Optional[int]
    emoji: Optional[str]
