from discord import (
    utils,
    CategoryChannel,
)
from sqlalchemy.future import select
from typing import List, Optional

from common.database import get_db, Setting, SettingsKey


async def get_channel_category(
    categories: List[CategoryChannel],
) -> Optional[CategoryChannel]:
    """
    Get the channel category for the guild
    :param categories: all the channel categories
    """
    # Get the channel category id
    async with get_db() as db:
        statement = select(Setting.value).where(
            Setting.key == SettingsKey.TicketCategory
        )
        result = await db.execute(statement)
    category_id = int(result.scalars().first())

    # Get the channel category
    return utils.get(categories, id=category_id)


async def get_ticket_roles() -> List[Setting]:
    """
    Get a list of the roles that can view a ticket
    """
    async with get_db() as db:
        statement = select(Setting).where(
            Setting.key.in_([SettingsKey.PanelAccessRole, SettingsKey.MentionRole])
        )
        result = await db.execute(statement)
        return result.scalars().all()
