from datetime import datetime
from discord import Embed, Member, User
from typing import List, Tuple, Union

from common.constants import EMBED_COLOR


def default(author: Union[Member, User], has_footer=True) -> Embed:
    """
    Generate an embed in the default format
    :param author: the command issuer
    :param has_footer: whether to add the footer and timestamp
    :return: the default embed format
    """
    # Set constants
    embed = Embed(color=EMBED_COLOR, type="rich")

    # Set the footer
    if has_footer:
        embed.set_footer(text=f"Requested by {author}", icon_url=str(author.avatar_url))
        embed.timestamp = datetime.now()

    return embed


def message(content) -> Embed:
    """
    Generate an embed for a text message
    :param content: the message content
    """
    # Create the base embed
    embed = Embed(color=EMBED_COLOR, type="rich")

    # Set the content
    embed.description = content

    return embed


def help_(
    prefix: str,
    author: Union[Member, User],
    name: str,
    explanations: List[Tuple[str, str]],
) -> Embed:
    """
    Generate a help embed for a command group
    :param prefix: the command prefix
    :param author: the command issuer
    :param name: the name of the command group
    :param explanations: a list of commands and their descriptions
    :return: a help embed
    """
    # Set the constants
    embed = default(author)
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
