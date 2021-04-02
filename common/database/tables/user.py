import sqlalchemy
from sqlalchemy.orm import relationship, Mapped
from typing import List, TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .message import Message
    from .ticket import Ticket


class User(Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, index=True)
    username = sqlalchemy.Column(sqlalchemy.String(37), nullable=False)
    avatar = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    has_panel = sqlalchemy.Column(sqlalchemy.Boolean, default=False, nullable=False)
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="creator")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="sender")
