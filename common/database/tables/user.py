import sqlalchemy

from .base import Base


class User(Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, index=True)
    username = sqlalchemy.Column(sqlalchemy.String(37), nullable=False)
    avatar = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    has_panel = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
