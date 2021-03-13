from typing import Optional

from .base import Model, find_primary_key
from ..tables import settings, SettingsKey


class Setting(Model):
    __table__ = settings
    __primary_key__ = find_primary_key(settings)

    id: Optional[int]
    key: SettingsKey
    value: str
