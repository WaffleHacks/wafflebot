from aiohttp import ClientSession
from datetime import datetime
from discord.ext.commands import Bot, Cog, Context, command
from functools import cached_property
from pydantic import BaseModel
from pytz import utc
from typing import Dict, List, Optional

from common import SETTINGS
from .. import embeds
from ..logger import get as get_logger

DESCRIPTION = "Get information about events during the hackathon"


class EventResponse(BaseModel):
    start_dt: datetime
    end_dt: datetime
    title: str
    notes: Optional[str]


class Events(Cog):
    def __init__(self, bot: Bot):
        self.logger = get_logger("extensions.events")
        self.bot = bot

        # Setup the HTTP session
        self.calendar = SETTINGS.bot.teamup_calendar
        self.__session = ClientSession(
            headers={"Teamup-Token": SETTINGS.bot.teamup_api_key},
            raise_for_status=True,
        )

        self.logger.info("loaded event commands")

    def cog_unload(self):
        # Close the session
        self.bot.loop.create_task(self.__shutdown_session())

        self.logger.info("unloaded event commands")

    async def __shutdown_session(self):
        await self.__session.close()

    @cached_property
    def query(self) -> Dict[str, str]:
        """
        Get the base query parameters for each request
        """
        start = SETTINGS.event_start.replace(tzinfo=utc).strftime("%Y-%m-%d")
        end = SETTINGS.event_end.replace(tzinfo=utc).strftime("%Y-%m-%d")
        return {
            "startDate": start,
            "endDate": end,
            "format": "markdown",
            "tz": "UTC",
        }

    async def list_events(self) -> List[EventResponse]:
        """
        Get a list of all the events
        """
        response = await self.__session.get(
            f"https://api.teamup.com/{self.calendar}/events", params=self.query
        )

        content = await response.json()
        events = content.get("events")
        if events is None:
            return []
        return list(map(EventResponse.parse_obj, events))

    @command()
    async def events(self, ctx: Context):
        """
        Get a list of all the events
        :param ctx: the command context
        """
        embed = embeds.message(
            "Here are all the events for this weekend!", as_title=True
        )
        embed.description = ""

        events = await self.list_events()
        for event in events:
            embed.description += (
                f"<t:{int(event.start_dt.strftime('%s'))}:f> - {event.title}\n"
            )

        await ctx.message.reply(mention_author=False, embed=embed)


def setup(bot: Bot):
    """
    Register the cog
    :param bot: the underlying bot
    """
    bot.add_cog(Events(bot))


def teardown(bot: Bot):
    """
    Unregister the cog
    :param bot: the underlying bot
    """
    bot.remove_cog("Events")
