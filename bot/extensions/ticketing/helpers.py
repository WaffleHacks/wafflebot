import asyncio
from discord import TextChannel

from common.database import get_db, Ticket


async def close_ticket(ticket_id: int, channel: TextChannel, wait: int):
    """
    Close a ticket and remove its channel
    :param ticket_id: the id of the ticket
    :param channel: the discord channel
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

    # Delete the channel
    await channel.delete()
