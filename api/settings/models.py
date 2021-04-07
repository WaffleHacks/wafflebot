from pydantic import BaseModel
from typing import List, Union

from common.config import ConfigKey


class SettingResponse(BaseModel):
    key: ConfigKey
    value: Union[List[str], str]


class SettingUpdate(BaseModel):
    value: Union[List[str], str]
