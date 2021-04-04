import asyncio
from datetime import datetime
from discord import (
    utils,
    AllowedMentions,
    CategoryChannel,
    Guild,
    Member,
    TextChannel,
    VoiceChannel,
)
from sqlalchemy.future import select
from typing import Optional, Tuple

from common import CONFIG
from common.database import get_db, Ticket
from bot import embeds
from .constants import NO_PERMISSIONS, TICKET_PERMISSIONS
from .helpers import create_user_if_not_exists, get_ticket_roles


async def archive_message(channel: TextChannel, executor_id: int):
    """
    Create the archive message
    :return:
    """
    guild = channel.guild

    # Get the channel
    archive_channel_id = await CONFIG.archive_channel()
    archive_channel = guild.get_channel(archive_channel_id)
    if archive_channel is None:
        return

    async with get_db() as db:
        # Get the ticket from the database
        result = await db.execute(select(Ticket).where(Ticket.channel_id == channel.id))
        ticket = result.scalars().first()
        if ticket is None:
            return

    # Create the embed
    embed = embeds.default(guild.me, has_footer=False)
    embed.title = "Ticket Closed"
    embed.add_field(name="Ticket ID", value=str(ticket.id), inline=True)
    embed.add_field(name="Opened By", value=f"<@{ticket.creator_id}>", inline=True)
    embed.add_field(name="Closed By", value=f"<@{executor_id}>", inline=True)
    # TODO: implement ticket log
    embed.add_field(name="Ticket Log", value="Click here", inline=True)
    embed.add_field(
        name="Opened At",
        value=ticket.created_at.strftime("%H:%M:%S %m/%d/%Y (UTC)"),
        inline=False,
    )
    embed.add_field(
        name="Closed At",
        value=datetime.utcnow().strftime("%H:%M:%S %m/%d/%Y (UTC)"),
        inline=False,
    )

    await archive_channel.send(embed=embed, allowed_mentions=AllowedMentions.none())


async def close_ticket(
    executor_id: int, text: TextChannel, voice: Optional[VoiceChannel], wait: int
):
    """
    Close a ticket and remove its channel
    :param executor_id: the id of the person executing the command
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

    # Send the archive message
    await archive_message(text, executor_id)


async def create_ticket(
    creator: Member,
    channel_category: CategoryChannel,
    guild: Guild,
    category_id: Optional[int],
    reason: Optional[str],
) -> Tuple[Ticket, TextChannel]:
    """
    Create a new ticket
    :param creator: the author of the ticket
    :param channel_category: the Discord category where the tickets reside
    :param guild: the discord server being executed in
    :param category_id: the ID of the category in the database. None when uncategorized
    :param reason: the reason for creating the ticket
    :return: the database ticket and the ticket channel
    """
    # Ensure the user exists in the database
    await create_user_if_not_exists(creator)

    # Add the ticket to the database
    async with get_db() as db:
        ticket = Ticket(
            category_id=category_id,
            creator_id=creator.id,
            is_open=True,
            reason=reason,
        )
        db.add(ticket)
        await db.commit()

    # Get the role(s) that can view tickets
    roles = await get_ticket_roles()
    authorized = [utils.get(guild.roles, id=role) for role in roles]
    authorized.append(creator)

    # Create the text channel within the category
    overwrites = {role: TICKET_PERMISSIONS for role in authorized}
    overwrites[guild.default_role] = NO_PERMISSIONS
    ticket_channel = await channel_category.create_text_channel(
        f"ticket-{ticket.id}", overwrites=overwrites
    )

    # Save the channel id
    async with get_db() as db:
        ticket.channel_id = ticket_channel.id
        db.add(ticket)
        await db.commit()

    # Ping the people for the ticket and instantly delete the message
    pingable_ids = await CONFIG.mention_role()
    pingable = [utils.get(guild.roles, id=pid) for pid in pingable_ids]
    pingable.append(creator)
    ping_message = " ".join([ping.mention for ping in pingable])
    ping = await ticket_channel.send(ping_message)
    await ping.delete()

    # Create the "welcome" embed
    # TODO: get embed content from DB
    embed = embeds.default(creator, has_footer=False)
    embed.title = "New Ticket"
    await ticket_channel.send(embed=embed)

    return ticket, ticket_channel
