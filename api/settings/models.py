from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Union

from common.config import ConfigKey


class SettingResponse(BaseModel):
    key: ConfigKey
    value: Union[List[int], int]


class SettingUpdate(BaseModel):
    value: Union[List[int], int]
