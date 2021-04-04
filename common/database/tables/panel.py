import sqlalchemy
from sqlalchemy.orm import relationship, Mapped
from typing import List, TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .reaction import Reaction


class Panel(Base):
    __tablename__ = "panels"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    message_id = sqlalchemy.Column(sqlalchemy.BigInteger, index=True)
    reactions: Mapped[List["Reaction"]] = relationship(
        "Reaction", back_populates="panel"
    )
    title = sqlalchemy.Column(sqlalchemy.String(256), nullable=False)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
