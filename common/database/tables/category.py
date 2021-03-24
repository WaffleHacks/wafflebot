import sqlalchemy
from sqlalchemy.orm import relationship, Mapped
from typing import List, TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .ticket import Ticket


class Category(Base):
    __tablename__ = "categories"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="category")
