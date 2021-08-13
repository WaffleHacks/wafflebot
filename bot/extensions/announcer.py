from datetime import datetime, timezone
from discord import TextChannel
from discord.ext import tasks
from discord.ext.commands import Bot, Cog
from sqlalchemy.future import select
from typing import List, Optional

from common import CONFIG, SETTINGS
from common.database import db_context, Announcement
from .. import embeds
from ..logger import get as get_logger


DESCRIPTION = "Automatically broadcast announcements at a given time"


class Announcer(Cog):
    def __init__(self, bot: Bot):
        self.logger = get_logger("extensions.announcer")
        self.bot = bot

        self.messages = []  # type: List[Announcement]
        self.channel: Optional[TextChannel] = None

        # Start the tasks
        self.refresh.start()
        self.check.start()

        self.logger.info("loaded announcer tasks")

    def cog_unload(self):
        self.refresh.stop()
        self.check.stop()

        self.logger.info("unloaded announcer tasks")

    @tasks.loop(minutes=5)
    async def refresh(self):
        """
        Refresh the internal message cache every 5 minutes
        """
        async with db_context() as db:
            statement = select(Announcement).where(
                Announcement.send_at >= datetime.now(timezone.utc)
            )
            result = await db.execute(statement)

        self.messages = result.scalars().all()

    @tasks.loop(minutes=1)
    async def check(self):
        """
        Check every minute if any messages in the internal cache need to be announced
        """
        for i, message in enumerate(self.messages):
            if message.send_at <= datetime.now(timezone.utc):
                await self.send(message)
                del self.messages[i]

    async def send(self, message: Announcement):
        """
        Announce a message
        :param message: the message object to announce
        """
        if self.channel is None:
            guild = await self.bot.fetch_guild(SETTINGS.discord_guild_id)
            channel_id = await CONFIG.announcements_channel()
            self.channel = await guild.fetch_channel(channel_id)

        if not message.embed:
            await self.channel.send(message.content)
            return

        embed = embeds.message(message.title, as_title=True)
        embed.description = message.content
        await self.channel.send(embed=embed)


def setup(bot: Bot):
    """
    Register the cog
    :param bot: the underlying bot
    """
    bot.add_cog(Announcer(bot))


def teardown(bot: Bot):
    """
    Unregister the cog
    :param bot: the underlying bot
    """
    bot.remove_cog("Announcer")
