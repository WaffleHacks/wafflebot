from pydantic import BaseModel
from typing import List, Union

from common.redis.kv import Key, Type


class SettingResponse(BaseModel):
    key: Key
    value: Union[List[str], str]
    type: Type


class SettingUpdate(BaseModel):
    value: Union[List[str], str]


class ChannelResponse(BaseModel):
    id: str
    name: str


class RoleResponse(BaseModel):
    id: str
    name: str
