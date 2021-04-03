import asyncio
from discord import (
    utils,
    CategoryChannel,
    Guild,
    Member,
    TextChannel,
    VoiceChannel,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from typing import Optional, Tuple

from common.database import get_db, SettingsKey, Ticket, User
from bot import embeds
from .constants import NO_PERMISSIONS, TICKET_PERMISSIONS
from .helpers import get_ticket_roles


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
    async with get_db() as db:
        user = User(
            id=creator.id,
            username=f"{creator.name}#{creator.discriminator}",
            avatar=str(creator.avatar_url),
            has_panel=True,
        )
        db.add(user)

        # Save the user, ignoring any users that already exist
        try:
            await db.commit()
        except IntegrityError:
            pass

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
    authorized = [utils.get(guild.roles, id=int(role.value)) for role in roles]
    authorized.append(creator)

    # Create the text channel within the category
    overwrites = {role: TICKET_PERMISSIONS for role in roles}
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
    ping_message = " ".join(
        [
            entity.mention
            for i, entity in enumerate(authorized)
            if type(entity) == Member or roles[i].key == SettingsKey.MentionRole
        ]
    )
    ping = await ticket_channel.send(ping_message)
    await ping.delete()

    # Create the "welcome" embed
    # TODO: get embed content from DB
    embed = embeds.default(creator, has_footer=False)
    embed.title = "New Ticket"
    await ticket_channel.send(embed=embed)

    return ticket, ticket_channel
