from pydantic import BaseModel
from typing import List, Union

from common.config import ConfigKey, Value


class SettingResponse(BaseModel):
    key: ConfigKey
    value: Union[List[str], str]
    type: Value


class SettingUpdate(BaseModel):
    value: Union[List[str], str]


class ChannelResponse(BaseModel):
    id: str
    name: str


class RoleResponse(BaseModel):
    id: str
    name: str
