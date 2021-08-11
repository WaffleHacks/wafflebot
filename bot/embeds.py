from discord import Embed
from typing import List, Tuple

from common.constants import EMBED_COLOR


def default() -> Embed:
    """
    Generate an embed in the default format
    :return: the default embed format
    """
    return Embed(color=EMBED_COLOR, type="rich")


def message(content: str, as_title=False) -> Embed:
    """
    Generate an embed for a text message
    :param content: the message content
    :param as_title: put the content in the title
    """
    embed = default()

    # Set the content
    if as_title:
        embed.title = content
    else:
        embed.description = content

    return embed


def error(title: str, content: str = "") -> Embed:
    """
    Generate an error embed
    :param title: the title for the embed
    :param content: the description of the error
    """
    embed = default()
    embed.title = f":x: {title}"
    embed.description = content
    return embed


def help_(
    prefix: str,
    name: str,
    explanations: List[Tuple[str, str]],
) -> Embed:
    """
    Generate a help embed for a command group
    :param prefix: the command prefix
    :param name: the name of the command group
    :param explanations: a list of commands and their descriptions
    :return: a help embed
    """
    # Set the constants
    embed = default()
    embed.description = "`<>` - required argument\n`[]` - optional argument"
    embed.title = f"{name.capitalize()} Help"

    # Add the help field
    embed.add_field(
        name=f"`{prefix}{name}`", value="display this help message", inline=False
    )

    # Add the explanations
    for command, explanation in explanations:
        embed.add_field(name=f"`{prefix}{command}`", value=explanation, inline=False)

    return embed
