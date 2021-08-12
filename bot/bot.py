from discord import Intents
from discord.ext.commands import (
    Bot,
    Context,
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    NoEntryPointError,
)
import os
from pathlib import Path

from common import SETTINGS
from . import logger, commands

logger.initialize()

# Initialize the bot
intents = Intents(guilds=True, members=True, messages=True, reactions=True)
bot = Bot(command_prefix="-", intents=intents, help_command=commands.Help())
bot.on_command_error = commands.on_error


# Block DMs globally
@bot.check
async def block_dms_globally(ctx: Context):
    return ctx.guild is not None


# Dynamically load extensions
extension_logger = logger.get("extensions")
extensions_path = Path(__file__).parent.joinpath("extensions")
for path in os.listdir(extensions_path):
    potential_import = extensions_path.joinpath(path)

    # Ignore files not ending in .py and package initializations
    if potential_import.is_file() and (
        not path.endswith(".py") or path == "__init__.py"
    ):
        continue

    # Ignore directories not containing __init__.py files
    if (
        potential_import.is_dir()
        and not potential_import.joinpath("__init__.py").exists()
    ):
        continue

    import_name = path.replace(".py", "")
    if import_name in SETTINGS.bot.disabled_extensions:
        extension_logger.info(f"skipping disabled extension '{import_name}'")
        continue

    # Create the qualified import name
    import_path = f"bot.extensions.{import_name}"

    # Attempt to load the extension
    try:
        bot.load_extension(import_path)
    except ExtensionAlreadyLoaded:
        extension_logger.warning(f"already loaded extension: '{import_path}'")
    except (ExtensionFailed, NoEntryPointError) as e:
        extension_logger.error(f"failed to load extension '{import_path}': {e}")
    except ExtensionNotFound:
        extension_logger.error(f"extension '{import_path}' could not be found")
