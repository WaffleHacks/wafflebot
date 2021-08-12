from discord import Client, Guild, Message, Object, TextChannel
from discord.errors import NotFound
from typing import Optional

from common import SETTINGS


DISCORD = Client()


def with_discord() -> Client:
    """
    Get a connection to discord
    """
    return DISCORD


async def get_channel(id_: int) -> Optional[TextChannel]:
    """
    Retrieve a channel by its ID
    :param id_: the channel's ID
    """
    try:
        channel = await DISCORD.fetch_channel(id_)
    except NotFound:
        return None
    if not isinstance(channel, TextChannel):
        return None

    # Populate the guild
    if type(channel.guild) == Object:
        channel.guild = await DISCORD.fetch_guild(channel.guild.id)

    return channel


async def get_message(channel: TextChannel, id_: int) -> Optional[Message]:
    """
    Retrieve a message by its ID
    :param channel: the containing channel
    :param id_: the ID of the message
    """
    try:
        return await channel.fetch_message(id_)
    except NotFound:
        return None
