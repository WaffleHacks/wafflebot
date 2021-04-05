from discord import TextChannel
from fastapi import HTTPException
import json
from pathlib import Path
import re
from typing import Dict

CHUNK_SIZE = 512
CUSTOM_EMOJI_REGEX = re.compile(r"<(a|):[a-z]{1,32}:\d+>")
DISCORD_EMOJI_MAPPING: Dict[str, str] = json.load(
    open(Path.cwd().joinpath("emojis.json"), "r")
)


async def validate_emoji(channel: TextChannel, potential_emoji: str) -> str:
    """
    Ensure that the emoji is valid
    :param channel: the panel's channel
    :param potential_emoji: the potential emoji string
    """
    # Determine if it could be a custom emoji
    if CUSTOM_EMOJI_REGEX.fullmatch(potential_emoji) is not None:
        # Get the emoji's id
        emoji_id = potential_emoji[potential_emoji.rfind(":") + 1 : -1]

        # Fetch the emoji
        emoji = await channel.guild.fetch_emoji(int(emoji_id))
        if emoji is None:
            raise HTTPException(status_code=400, detail="custom emoji does not exist")

        return str(emoji)

    # Check if the emoji is a standard one
    if potential_emoji not in DISCORD_EMOJI_MAPPING:
        raise HTTPException(status_code=400, detail="invalid emoji name")

    return DISCORD_EMOJI_MAPPING[potential_emoji]
