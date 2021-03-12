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

from . import logger, commands

logger.initialize()

# Initialize the bot
intents = Intents(guilds=True, members=True, messages=True, reactions=True)
bot = Bot(command_prefix=".", intents=intents, help_command=commands.Help())
bot.on_command_error = commands.on_error


# Block DMs globally
@bot.check
async def block_dms_globally(ctx: Context):
    return ctx.guild is not None


# Dynamically load extensions
extension_logger = logger.get("extensions")
extensions_path = Path(__file__).parent.joinpath("extensions")
for file in os.listdir(extensions_path):
    # Skip non-python files and __init__.py
    if not file.endswith(".py") or file == "__init__.py":
        continue

    # Create the qualified import name
    import_name = f"bot.extensions.{file[:-3]}"

    # Attempt to load the extension
    try:
        bot.load_extension(import_name)
    except ExtensionAlreadyLoaded:
        extension_logger.warning(f"already loaded extension: '{import_name}'")
    except (ExtensionFailed, NoEntryPointError) as e:
        extension_logger.error(f"failed to load extension '{import_name}': {e}")
    except ExtensionNotFound:
        extension_logger.error(f"extension '{import_name}' could not be found")
