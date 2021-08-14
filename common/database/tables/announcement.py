import sqlalchemy

from .base import Base
from .types import TimeStamp


class Announcement(Base):
    __tablename__ = "announcements"
    __table_args__ = (
        sqlalchemy.CheckConstraint(
            "embed = false OR (embed = true AND title IS NOT NULL)"
        ),
    )

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    send_at = sqlalchemy.Column(TimeStamp(timezone=True), nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String(128), nullable=False)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    embed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    title = sqlalchemy.Column(sqlalchemy.String(256), nullable=True)
