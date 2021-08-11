from discord.ext.commands import (
    Bot,
    Context,
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    ExtensionNotLoaded,
    group,
    NoEntryPointError,
)

from .. import embeds
from ..logger import get as get_logger
from ..permissions import has_role, ConfigKey

DESCRIPTION = "Commands for managing the bot"

logger = get_logger("extensions.management")


@group()
@has_role(ConfigKey.ManagementRole)
async def management(ctx: Context):
    """
    Extensions management group
    :param ctx: the command context
    """
    if ctx.invoked_subcommand is None:
        await ctx.reply(
            embed=embeds.help_(
                ctx.bot.command_prefix,
                "management",
                [
                    ("management enable <package>", "enable an extension"),
                    (
                        "management reload <package>",
                        "disable and re-enable an extension",
                    ),
                    ("management disable <package>", "disable an extension"),
                    ("management list", "list all the enabled extensions"),
                ],
            ),
            mention_author=False,
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
        await ctx.reply(
            embed=embeds.message(f"Enabled extension `{package}`!"),
            mention_author=False,
        )
    except ExtensionAlreadyLoaded:
        logger.warning(f"already loaded extension '{package}'")
        await ctx.reply(
            embed=embeds.message(f"That extension is already enabled!"),
            mention_author=False,
        )
    except (ExtensionFailed, NoEntryPointError) as e:
        logger.error(f"failed to load extension '{package}': {e}")
        await ctx.reply(
            embed=embeds.message(
                f"An error occurred while enabling extension `{package}`: {e}."
            ),
            mention_author=False,
        )
    except ExtensionNotFound:
        logger.error(f"extension '{package}' could not be found")
        await ctx.reply(
            embed=embeds.message(
                f"Couldn't find extension `{package}`, check the name and try again."
            ),
            mention_author=False,
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
        await ctx.reply(
            embed=embeds.message(f"Reloaded extension `{package}`!"),
            mention_author=False,
        )
    except ExtensionNotFound:
        logger.error(f"extension '{package}' could not be found")
        await ctx.reply(
            embed=embeds.message(
                f"Couldn't find extension `{package}`, check the name and try again."
            ),
            mention_author=False,
        )
    except (ExtensionFailed, NoEntryPointError) as e:
        logger.error(f"failed to load extension '{package}': {e}")
        await ctx.reply(
            embed=embeds.message(f"Failed to load extension: `{package}`: {e}."),
            mention_author=False,
        )
    except ExtensionNotLoaded:
        logger.error(f"extension '{package}' is not loaded")
        await ctx.reply(
            embed=embeds.message(f"Cannot reload disabled extension `{package}`."),
            mention_author=False,
        )


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
        await ctx.reply(
            embed=embeds.message(f"Disabled extension `{package}`!"),
            mention_author=False,
        )
    except ExtensionNotLoaded:
        logger.error(f"extension '{package}' is not loaded")
        await ctx.reply(
            embed=embeds.message(f"Cannot disable a disabled extension `{package}`."),
            mention_author=False,
        )


@management.command(name="list")
async def list_extensions(ctx: Context):
    """
    Get a list of all the loaded extensions
    :param ctx: the command context
    """
    # Build the base response
    embed = embeds.default()
    embed.title = "Enabled Extensions"

    # Add all the extension names
    for extension, module in ctx.bot.extensions.items():
        # Attempt to get the extension description
        try:
            description = module.DESCRIPTION
        except AttributeError:
            description = "no description provided"

        name = extension[extension.rfind(".") + 1 :]
        embed.add_field(name=f"`{name}`", value=description)

    await ctx.reply(embed=embed, mention_author=False)


def setup(bot: Bot):
    bot.add_command(management)
    logger.info("loaded management commands")


def teardown(bot: Bot):
    bot.remove_command("management")
    logger.info("unloaded management commands")
