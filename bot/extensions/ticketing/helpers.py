import asyncio
from discord import TextChannel, VoiceChannel
from typing import Optional

from common.database import get_db, Ticket


async def close_ticket(
    ticket_id: int, text: TextChannel, voice: Optional[VoiceChannel], wait: int
):
    """
    Close a ticket and remove its channel
    :param ticket_id: the id of the ticket
    :param text: the discord text channel
    :param voice: an optional discord voice channel
    :param wait: the number of seconds to wait before deleting
    """
    # Wait before deleting the ticket
    await asyncio.sleep(wait)

    async with get_db() as db:
        # Retrieve the ticket from the database
        ticket = await db.get(Ticket, ticket_id)
        if ticket is None:
            return

        # Mark the ticket as closed
        ticket.is_open = False
        await db.commit()

    # Delete the channels
    await text.delete()
    if voice is not None:
        await voice.delete()
