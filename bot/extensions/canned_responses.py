from discord import Message
from discord.ext.commands import Bot, Cog
import json
from sqlalchemy.future import select

from common.database import get_db, CannedResponse as Canned
from .. import embeds
from ..logger import get as get_logger

DESCRIPTION = "Pre-made responses for commonly requested information"


class CannedResponses(Cog):
    def __init__(self):
        self.logger = get_logger("extensions.canned_responses")
        self.logger.info("loaded canned response commands")

    def cog_unload(self):
        self.logger.info("unloaded canned response commands")

    @Cog.listener()
    async def on_message(self, message: Message):
        # Ignore self messages and non trigger messages
        if message.author.bot or not message.content.startswith("."):
            return

        # Attempt to get the message
        key = message.content[1:]
        async with get_db() as db:
            statement = select(Canned).where(Canned.key == key)
            result = await db.execute(statement)
        response = result.scalars().first()

        # Don't respond if no model
        if response is None:
            self.logger.info(f"requested canned response '{key}' does not exist")
            return

        # Build the response
        embed = embeds.default(message.author)
        embed.title = response.title
        embed.description = response.content

        # Add fields if exists
        fields = json.loads(response.fields)
        for name, content in fields.items():
            embed.add_field(name=name, value=content, inline=False)

        await message.channel.send(embed=embed)
        self.logger.info(f"generated response for '{key}'")


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
