from discord import utils, CategoryChannel, Guild, Role, TextChannel
from discord.ext.commands import group, Bot, Context, Greedy
from enum import Enum
from typing import List, Optional, Union

from common import CONFIG, ConfigKey
from .. import embeds
from ..logger import get as get_logger
from ..permissions import has_role

DESCRIPTION = "Change the bot's settings"

logger = get_logger("extensions.settings")


class Action(Enum):
    """
    The possible actions when using a command
    """

    Get = "get"
    Set = "set"
    Add = "add"
    Remove = "remove"


def resolve_object(
    guild: Guild, object_id: int
) -> Optional[Union[CategoryChannel, TextChannel, Role]]:
    """
    Retrieve a discord object from its id
    :param guild: the server to fetch data from
    :param object_id: the object's ID
    :return: an optional resolved object
    """
    # Attempt to get it as a role
    role = utils.get(guild.roles, id=object_id)
    if role is not None:
        return role

    # Attempt to get it as a text channel
    text = utils.get(guild.channels, id=object_id)
    if text is not None and isinstance(text, TextChannel):
        return text

    # Attempt to get it as a category
    return utils.get(guild.categories, id=object_id)


async def single_config_helper(
    ctx: Context,
    name: str,
    action: Action,
    value: Optional[Union[CategoryChannel, TextChannel, Role]],
):
    """
    A helper method to reduce the amount of duplicated code when setting/getting a config value
    :param ctx: the command context
    :param name: the name of the value being set
    :param action: the action run
    :param value: the value to (maybe) set
    """
    attr_name = name.replace(" ", "_")
    attr_type = name.split(" ")[-1]

    # Ensure valid action
    if action == Action.Add or action == Action.Remove:
        await ctx.channel.send(
            embed=embeds.message(f":x: Cannot add to/remove from non-array config key")
        )
        return

    # Get the current value
    elif action == Action.Get:
        result_id = await getattr(CONFIG, attr_name)()
        result = resolve_object(ctx.guild, result_id)
        if result is None:
            await ctx.channel.send(
                embed=embeds.message(
                    f"The {name} is currently set to `{result_id}`, but the {attr_type} may not exist."
                )
            )
        else:
            await ctx.channel.send(
                embed=embeds.message(f"The {name} is currently {result.mention}."),
                allowed_mentions=None,
            )

    # Set the current value
    else:
        # Ensure a value is provided
        if value is None:
            await ctx.channel.send(
                embed=embeds.message(f":x: A {attr_type} to set must be provided!")
            )
            return

        # Set the value
        await getattr(CONFIG, attr_name)(value.id)
        await ctx.channel.send(
            embed=embeds.message(
                f":white_check_mark: The {name} is now {value.mention}"
            ),
            allowed_mentions=None,
        )


async def send_config_array(ctx: Context, name: str, attr_name: str):
    """
    Get and send an array of config values
    :param ctx: the command context
    :param name: the parameter name
    :param attr_name: the function to call
    """
    # Get the ids
    result_ids = await getattr(CONFIG, attr_name)()

    # Construct the resulting message
    message = f"The {name} are currently set to: "
    for result_id in result_ids:
        result = resolve_object(ctx.guild, result_id)
        if result is None:
            message += f"`{result_id}` (may not exist), "
        else:
            message += f"{result.mention}, "

    # Send it
    await ctx.channel.send(embed=embeds.message(message[:-2]), allowed_mentions=None)


async def array_config_helper(
    ctx: Context, name: str, action: Action, values: Optional[Union[Role, List[Role]]]
):
    """
    A helper method to reduce the amount of duplicated code when setting/getting an array of config values
    :param ctx: the command context
    :param name: the pluralized name of the config
    :param action: the action run
    :param values: the value(s) to set/add/remove
    """
    attr_name = name.replace(" ", "_")
    attr_type = name.split(" ")[-1]

    # Get the current values
    if action == Action.Get:
        await send_config_array(ctx, name, attr_name)

    # Ensure there is at least 1 value present
    elif values is None:
        await ctx.channel.send(
            embed=embeds.message(f":x: At least 1 {attr_type} must be provided!")
        )

    # Add/remove/set the value(s)
    else:
        # Convert the value(s) to ids
        if not isinstance(values, list):
            values = [values]
        value_ids = [value.id for value in values]

        # Determine the method to call
        method = {
            Action.Set: "set_{}",
            Action.Add: "add_{}",
            Action.Remove: "remove_{}",
        }[action].format(attr_name)

        # Run the action
        await getattr(CONFIG, method)(value_ids)

        # Display the updated values
        await send_config_array(ctx, name, attr_name)


@group()
@has_role(ConfigKey.PanelAccessRole)
async def settings(ctx: Context):
    """
    Settings management group
    :param ctx: the command context
    """
    if ctx.invoked_subcommand is None:
        await ctx.channel.send(
            embed=embeds.help_(
                ctx.bot.command_prefix,
                ctx.author,
                "settings",
                [
                    (
                        "settings management-role <get|set> [role]",
                        "modify who can configure the bot",
                    ),
                    (
                        "settings panel-access-role <get|set> [role]",
                        "modify the roles which have access to the panel",
                    ),
                    (
                        "settings registered-role <get|set> [role]",
                        "modify the role marking a participant as registered in hackathon manager",
                    ),
                ],
            )
        )


@settings.command(name="management-role")
@has_role(ConfigKey.ManagementRole)
async def management_role(ctx: Context, action: Action, value: Optional[Role]):
    """
    Get/set the bot management role
    :param ctx: the command context
    :param action: what to do with the key
    :param value: the optional value to set
    """
    await single_config_helper(ctx, "management role", action, value)


@settings.command(name="panel-access-role")
async def panel_access_role(ctx: Context, action: Action, value: Optional[Role]):
    """
    Get/set the role that has access to the panel
    :param ctx: the command context
    :param action: what to do with the key
    :param value: the optional value to set
    """
    await single_config_helper(ctx, "panel access role", action, value)


@settings.command(name="registered-role")
async def registered_role(ctx: Context, action: Action, value: Optional[Role]):
    """
    Get/set the role that marks a participant as verified
    :param ctx: the command context
    :param action: what to do with the key
    :param value: the optional value to set
    """
    await single_config_helper(ctx, "registered role", action, value)


def setup(bot: Bot):
    """
    Register the commands with the bot
    :param bot: the underlying bot
    """
    bot.add_command(settings)
    logger.info("loaded settings commands")


def teardown(bot: Bot):
    """
    De-register the commands with the bot
    :param bot: the underlying bot
    """
    bot.remove_command("settings")
    logger.info("unloaded settings commands")
