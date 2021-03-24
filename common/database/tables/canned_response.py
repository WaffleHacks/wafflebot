import sqlalchemy
from sqlalchemy.dialects import postgresql

from .base import Base


class CannedResponse(Base):
    __tablename__ = "canned_responses"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    key = sqlalchemy.Column(
        sqlalchemy.String(32), nullable=False, index=True, unique=True
    )
    title = sqlalchemy.Column(sqlalchemy.String(256), nullable=False)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    fields = sqlalchemy.Column(postgresql.JSON, nullable=False)
