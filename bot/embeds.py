from datetime import datetime
from discord import Color, Embed, Member
from typing import List, Tuple

EMBED_COLOR = Color.from_rgb(0, 0, 0)


def default_embed(author: Member) -> Embed:
    """
    Generate an embed in the default format
    :param author: the command issuer
    :return: the default embed format
    """
    # Set constants
    embed = Embed(color=EMBED_COLOR, timestamp=datetime.now(), type="rich")

    # Set the footer
    embed.set_footer(text=f"Requested by {author}", icon_url=str(author.avatar_url))

    return embed


def help_embed(author: Member, name: str, explanations: List[Tuple[str, str]]) -> Embed:
    """
    Generate a help embed for a command group
    :param author: the command issuer
    :param name: the name of the command group
    :param explanations: a list of commands and their descriptions
    :return: a help embed
    """
    # Set the constants
    embed = default_embed(author)
    embed.description = "`<>` - required argument\n`[]` - optional argument"
    embed.title = f"{name.capitalize()} Help"

    # Add the help field
    embed.add_field(name=f"`.{name}`", value="display this help message", inline=False)

    # Add the explanations
    for command, explanation in explanations:
        embed.add_field(name=f"`{command}`", value=explanation, inline=False)

    return embed
