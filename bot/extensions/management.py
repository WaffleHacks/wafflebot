from discord.ext.commands import (
    Bot,
    Context,
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    ExtensionNotLoaded,
    group,
    is_owner,
    NoEntryPointError,
)

from .. import embeds
from ..logger import get as get_logger

DESCRIPTION = "Commands for managing the bot"

logger = get_logger("extensions.management")


@group()
@is_owner()
async def management(ctx: Context):
    """
    Extensions management group
    :param ctx: the command context
    """
    if ctx.invoked_subcommand is None:
        await ctx.channel.send(
            embed=embeds.help_(
                ctx.author,
                "management",
                [
                    (".management enable <package>", "enable an extension"),
                    (
                        ".management reload <package>",
                        "disable and re-enable an extension",
                    ),
                    (".management disable <package>", "disable an extension"),
                    (".management list", "list all the enabled extensions"),
                ],
            )
        )


@management.command(name="enable")
async def enable_extension(ctx: Context, package: str):
    """
    Load and enable an extension
    :param ctx: the command context
    :param package: the extension's name
    """
    import_name = f"bot.extensions.{package}"
    try:
        ctx.bot.load_extension(import_name)
        await ctx.channel.send(f"Enabled extension `{package}`!")
    except ExtensionAlreadyLoaded:
        logger.warning(f"already loaded extension '{package}'")
        await ctx.channel.send(f"That extension is already enabled!")
    except (ExtensionFailed, NoEntryPointError) as e:
        logger.error(f"failed to load extension '{package}': {e}")
        await ctx.channel.send(
            f"An error occurred while enabling extension `{package}`: {e}."
        )
    except ExtensionNotFound:
        logger.error(f"extension '{package}' could not be found")
        await ctx.channel.send(
            f"Couldn't find extension `{package}`, check the name and try again."
        )


@management.command(name="reload")
async def reload_extension(ctx: Context, package: str):
    """
    Reload an extension
    :param ctx: the command context
    :param package: the extension's name
    """
    import_name = f"bot.extensions.{package}"
    try:
        ctx.bot.reload_extension(import_name)
    except ExtensionNotFound:
        logger.error(f"extension '{package}' could not be found")
        await ctx.channel.send(
            f"Couldn't find extension `{package}`, check the name and try again."
        )
    except (ExtensionFailed, NoEntryPointError) as e:
        logger.error(f"failed to load extension '{package}': {e}")
        await ctx.channel.send(f"Failed to load extension: `{package}`: {e}.")
    except ExtensionNotLoaded:
        logger.error(f"extension '{package}' is not loaded")
        await ctx.channel.send(f"Cannot reload disabled extension `{package}`.")


@management.command(name="disable")
async def disable_extension(ctx: Context, package: str):
    """
    Disable and unload an extension
    :param ctx: the command context
    :param package: the extension's name
    """
    import_name = f"bot.extensions.{package}"
    try:
        ctx.bot.unload_extension(import_name)
        await ctx.channel.send(f"Disabled extension `{package}`!")
    except ExtensionNotLoaded:
        logger.error(f"extension '{package}' is not loaded")
        await ctx.channel.send(f"Cannot disable a disabled extension `{package}`.")


@management.command(name="list")
async def list_extensions(ctx: Context):
    """
    Get a list of all the loaded extensions
    :param ctx: the command context
    """
    # Build the base response
    embed = embeds.default(ctx.author)
    embed.title = "Enabled Extensions"

    # Add all the extension names
    for extension, module in ctx.bot.extensions.items():
        # Attempt to get the extension description
        try:
            description = module.DESCRIPTION
        except AttributeError:
            description = "no description provided"

        embed.add_field(name=f"`{extension}`", value=description)

    await ctx.channel.send(embed=embed)


def setup(bot: Bot):
    bot.add_command(management)
    logger.info("loaded management commands")


def teardown(bot: Bot):
    bot.remove_command("management")
    logger.info("unloaded management commands")
