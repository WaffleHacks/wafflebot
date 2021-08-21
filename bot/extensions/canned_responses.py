from discord import Message
from discord.ext.commands import Bot, Cog
from sqlalchemy.future import select

from common.database import db_context, CannedResponse as Canned
from .. import embeds, logger

DESCRIPTION = "Pre-made responses for commonly requested information"
LOGGER = logger.get("extensions.canned_responses")


class CannedResponses(Cog):
    def __init__(self):
        LOGGER.info("loaded canned response commands")

    def cog_unload(self):
        LOGGER.info("unloaded canned response commands")

    @Cog.listener()
    async def on_message(self, message: Message):
        # Ignore self messages and non trigger messages
        if message.author.bot or not message.content.startswith("."):
            return

        # Attempt to get the message
        key = message.content[1:]
        async with db_context() as db:
            statement = select(Canned).where(Canned.key == key)
            result = await db.execute(statement)
        response = result.scalars().first()

        # Don't respond if no model
        if response is None:
            LOGGER.info(f"requested canned response '{key}' does not exist")
            return

        # Build the response
        embed = embeds.default()
        embed.title = response.title
        embed.description = response.content

        # Add fields if exists
        for name, content in response.fields.items():
            embed.add_field(name=name, value=content, inline=False)

        await message.reply(embed=embed, mention_author=False)
        LOGGER.info(f"sent response for '{key}'")


def setup(bot: Bot):
    """
    Register the cog
    :param bot: the underlying bot
    """
    bot.add_cog(CannedResponses())


def teardown(bot: Bot):
    """
    Unregister the cog
    :param bot: the underlying bot
    """
    bot.remove_cog("CannedResponses")
