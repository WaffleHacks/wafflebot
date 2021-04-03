import asyncio
from discord import utils, CategoryChannel, TextChannel, VoiceChannel
from sqlalchemy.future import select
from typing import List, Optional

from common.database import get_db, Setting, SettingsKey, Ticket


async def close_ticket(text: TextChannel, voice: Optional[VoiceChannel], wait: int):
    """
    Close a ticket and remove its channel
    :param text: the discord text channel
    :param voice: an optional discord voice channel
    :param wait: the number of seconds to wait before deleting
    """
    # Wait before deleting the ticket
    await asyncio.sleep(wait)

    async with get_db() as db:
        # Retrieve the ticket from the database
        statement = select(Ticket).where(Ticket.channel_id == text.id)
        result = await db.execute(statement)
        ticket = result.scalars().first()

        # Mark the ticket as closed
        ticket.is_open = False
        await db.commit()

    # Delete the channels
    await text.delete()
    if voice is not None:
        await voice.delete()


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
