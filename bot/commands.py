from discord.ext.commands import (
    Bot,
    CheckFailure,
    Command,
    CommandNotFound,
    Context,
    Group,
    HelpCommand,
    MemberNotFound,
    MissingRequiredArgument,
)
import re
from typing import get_type_hints

from . import logger
from .embeds import default_embed


async def on_error(ctx: Context, exception: Exception):
    """
    Handle errors generated from commands
    :param ctx: the command context
    :param exception: the thrown exception
    """
    exception_type = type(exception)

    # Ignore failures from checks and command not found errors
    if exception_type == CheckFailure or exception_type == CommandNotFound:
        return

    # Notify of non-existent user
    elif exception_type == MemberNotFound:
        await ctx.channel.send(f"Could not find member `{exception.argument}`")

    # Notify of missing parameter
    elif exception_type == MissingRequiredArgument:
        formatted = str(exception)
        arg_separator = formatted.index(" ")
        await ctx.channel.send(
            f"`{formatted[:arg_separator]}`{formatted[:arg_separator]}"
            f" Use `.help {ctx.command.qualified_name}` for usage information"
        )

    # Log the error
    else:
        logger.get().error(f"{type(exception).__name__}: {exception}")
        await ctx.channel.send("An internal error occurred, please try again later")


class Help(HelpCommand):
    __OPTIONAL_REGEX = re.compile(r"typing\.Union\[[a-zA-Z0-9.]+, NoneType]")

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot  # type: Bot

        # Create the base embed
        embed = default_embed(ctx.author)
        embed.title = "WaffleBot Help"
        embed.description = "All available commands:"

        # Split the commands into left and right columns
        filtered = await self.filter_commands(bot.commands, sort=True)
        partition = len(filtered) // 2 + 1
        left = filtered[:partition]
        right = filtered[partition:]

        # Add the commands to the help menu
        for side in [left, right]:
            text = ""

            for command in side:
                text += f"`{bot.command_prefix}{command.qualified_name}`\n"

            embed.add_field(name="\u200b", value=text.strip("\n"), inline=True)

        # Add the footer
        embed.add_field(
            name="\u200b",
            value=f"Type `{bot.command_prefix}help <command>` for information on a command.",
            inline=False,
        )

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command: Command):
        ctx = self.context
        bot = ctx.bot  # type: Bot

        # Create the base embed
        embed = default_embed(ctx.author)
        embed.title = f"`{bot.command_prefix}{command.qualified_name}` Help"
        embed.description = "`<>` - required argument\n`[]` - optional argument"

        # Reformat the docstring
        if command.help is None:
            embed.add_field(
                name="Description",
                value="No description or usage information was provided",
            )
        else:
            # Create the new description
            description = ""
            for line in command.help.split("\n"):
                if line.startswith(":") or line == "":
                    break
                description += line
            embed.add_field(name="Description", value=description, inline=False)

            # Create the usage information
            usage = f"`{bot.command_prefix}{command.qualified_name}"
            hints = get_type_hints(command.callback)

            # Parse the parameters
            for parameter, hint in hints.items():
                # Ignore the context parameter
                if parameter == "ctx":
                    continue

                # Add optional and required arguments
                if self.__OPTIONAL_REGEX.fullmatch(str(hint)) is None:
                    usage += f" <{parameter}>"
                else:
                    usage += f" [{parameter}]"

            embed.add_field(name="Usage", value=usage + "`", inline=False)

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group: Group):
        await group.invoke(self.context)
