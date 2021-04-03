from enum import Enum
import sqlalchemy

from .base import Base


class SettingsKey(Enum):
    ManagementRole = 1
    PanelAccessRole = 2
    MentionRole = 3
    TicketCategory = 4


class Setting(Base):
    __tablename__ = "settings"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    key = sqlalchemy.Column(sqlalchemy.Enum(SettingsKey), nullable=False, index=True)
    value = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
