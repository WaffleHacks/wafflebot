from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Union

from common.config import ConfigKey


class SettingResponse(BaseModel):
    key: ConfigKey
    value: Union[List[int], int]


class UpdateAction(Enum):
    Add = "add"
    Remove = "remove"


class SettingUpdate(BaseModel):
    action: Optional[UpdateAction]
    value: Union[List[int], int]
