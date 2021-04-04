from datetime import datetime
import sqlalchemy
from sqlalchemy.orm import relationship, Mapped
from typing import List, TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .category import Category
    from .message import Message
    from .user import User


class Ticket(Base):
    __tablename__ = "tickets"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    channel_id = sqlalchemy.Column(sqlalchemy.BigInteger, index=True)
    category_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("categories.id"), nullable=True
    )
    category: "Category" = relationship("Category", back_populates="tickets")
    creator_id = sqlalchemy.Column(
        sqlalchemy.BigInteger, sqlalchemy.ForeignKey("users.id"), nullable=False
    )
    creator: "User" = relationship("User", back_populates="tickets")
    is_open = sqlalchemy.Column(sqlalchemy.Boolean, default=True, nullable=False)
    reason = sqlalchemy.Column(sqlalchemy.String(256), nullable=True)
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime, nullable=True, default=datetime.utcnow()
    )
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="ticket")
