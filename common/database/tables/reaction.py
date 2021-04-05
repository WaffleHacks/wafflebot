import sqlalchemy
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .category import Category
    from .panel import Panel


class Reaction(Base):
    __tablename__ = "reactions"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    emoji = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    category_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    category: "Category" = relationship("Category", back_populates="reactions")
    panel_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("panels.id", ondelete="CASCADE"),
        nullable=False,
    )
    panel: "Panel" = relationship("Panel", back_populates="reactions")
