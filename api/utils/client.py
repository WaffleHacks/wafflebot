from discord import Client, TextChannel
from fastapi import HTTPException


DISCORD = Client()


def with_discord() -> Client:
    """
    Get a connection to discord
    """
    return DISCORD


async def get_channel(id_: int) -> TextChannel:
    """
    Retrieve a channel, ensuring that it exists
    :param id_: the channel's ID
    """
    channel = await DISCORD.fetch_channel(id_)
    if channel is None:
        raise HTTPException(status_code=400, detail="could not find specified channel")
    elif not isinstance(channel, TextChannel):
        raise HTTPException(status_code=400, detail="channel must be a text channel")

    # Populate the guild
    channel.guild = await DISCORD.fetch_guild(channel.guild.id)

    return channel
