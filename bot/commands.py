from discord.ext.commands import (
    Bot,
    CheckFailure,
    Command,
    CommandError,
    CommandNotFound,
    Context,
    Group,
    HelpCommand,
    MemberNotFound,
    MissingRequiredArgument,
)
import re
from sentry_sdk import capture_exception
import sys
import traceback
from typing import get_type_hints, Dict, List, Tuple

from common import SETTINGS
from . import logger, embeds


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
        await ctx.reply(
            embed=embeds.error(
                "Unknown member", f"Could not find member `{exception.argument}`"
            ),
            mention_author=False,
        )

    # Notify of missing parameter
    elif exception_type == MissingRequiredArgument:
        formatted = str(exception)
        arg_separator = formatted.index(" ")
        await ctx.reply(
            embed=embeds.error(
                f"`{formatted[:arg_separator]}`{formatted[arg_separator:]}",
                f"Use `{ctx.bot.command_prefix}help {ctx.command.qualified_name}` for usage information",
            ),
            mention_author=False,
        )

    else:
        # Log the error
        name = "extensions." + ctx.command.name if ctx.command else ""
        logger.get(name).error(f"{type(exception).__name__}: {exception}")

        capture_exception(exception)

        # Log the full traceback if enabled
        if SETTINGS.full_errors:
            traceback.print_exception(
                type(exception), exception, exception.__traceback__, file=sys.stdout
            )

        # Notify the user
        await ctx.reply(
            embed=embeds.error(
                "Unknown exception",
                "An internal error occurred, please try again later",
            ),
            mention_author=False,
        )


class Help(HelpCommand):
    __OPTIONAL_REGEX = re.compile(r"typing\.Union\[[a-zA-Z0-9.]+, NoneType]")

    def get_destination(self):
        return self.context.message

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot  # type: Bot

        # Create the base embed
        embed = embeds.default()
        embed.title = "WaffleBot Help"
        embed.description = "All available commands:"

        # Split the commands into left and right columns
        filtered = await self.filter_all_commands(bot.all_commands)
        partition = (len(filtered) // 2) + (len(filtered) % 2)
        left = filtered[:partition]
        right = filtered[partition:]

        # Add the commands to the help menu
        for side in [left, right]:
            text = ""

            for name, command in side:
                text += f"`{bot.command_prefix}{name}`\n"

            if text != "":
                embed.add_field(name="\u200b", value=text.strip("\n"), inline=True)

        # Add the footer
        embed.add_field(
            name="\u200b",
            value=f"Type `{bot.command_prefix}help <command>` for information on a command.",
            inline=False,
        )

        await self.get_destination().reply(embed=embed, mention_author=False)

    async def send_command_help(self, command: Command):
        ctx = self.context
        bot = ctx.bot  # type: Bot

        # Check if using a command alias
        requested_command = " ".join(ctx.message.content.split(" ")[1:])
        name = command.name
        if requested_command != command.name:
            name = requested_command

        # Create the base embed
        embed = embeds.default()
        embed.title = f"`{bot.command_prefix}{name}` Help"
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
            usage = f"`{bot.command_prefix}{name}"
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

        await self.get_destination().reply(embed=embed, mention_author=False)

    async def send_group_help(self, group: Group):
        await group.invoke(self.context)

    async def filter_all_commands(
        self, commands: Dict[str, Command]
    ) -> List[Tuple[str, Command]]:
        """
        Returns the largest name length of the specified command list, including aliases.
        :param commands: all the commands to check
        :return: The maximum width of the commands
        """
        # Remove hidden commands
        iterator = (
            commands.items()
            if self.show_hidden
            else filter(lambda item: not item[1].hidden, commands.items())
        )

        # Check every command if it can run
        async def predicate(c: Command):
            try:
                return await c.can_run(self.context)
            except CommandError:
                return False

        # Check each command
        ret = []
        for name, cmd in iterator:
            valid = await predicate(cmd)
            if valid:
                ret.append((name, cmd))

        # Sort the commands by name
        ret.sort(key=lambda item: item[0])
        return ret
