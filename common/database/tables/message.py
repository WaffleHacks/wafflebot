from datetime import datetime
import sqlalchemy
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .ticket import Ticket
    from .user import User


class Message(Base):
    __tablename__ = "messages"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    ticket_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("tickets.id"), nullable=False
    )
    ticket: "Ticket" = relationship("Ticket", back_populates="messages")
    sender_id = sqlalchemy.Column(
        sqlalchemy.BigInteger, sqlalchemy.ForeignKey("users.id"), nullable=False
    )
    sender: "User" = relationship("User", back_populates="messages")
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime, nullable=True, default=datetime.utcnow()
    )
