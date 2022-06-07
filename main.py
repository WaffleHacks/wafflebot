import aiohttp
import interactions
from datetime import datetime

from aiohttp import ClientSession
from pydantic import BaseModel
from pytz import utc
from typing import Dict, List, Optional
class EventResponse(BaseModel):
    start_dt: datetime
    end_dt: datetime
    title: str
    notes: Optional[str]

bot = interactions.Client(token="OTgwMjEzNjc1MTA3NDI2MzI1.Gf8n-j.h5s8VbTt26lhEcwx2T_suKKdC2Ag6Z8LqucLxk")

calender_id = 'kso6qzsg1puo4x3kjq'
start= '2022-06-17'
end= '2022-06-19'
teamup_api_key= '02e35b2e336ee18b7fe35c4f9f5483bb5b3a473bec6e144eddaf428833f92b5c'
async def list_events() -> List[EventResponse]:
    """
    Get a list of all the events
     :param ctx: the command context"""
    async with aiohttp.ClientSession(headers={"Teamup-Token": teamup_api_key},
            raise_for_status=True,) as session:
        response = await session.get(
            f"https://api.teamup.com/{calender_id}/events", params= {
            "startDate": start,
            "endDate": end,
            "format": "markdown",
            "tz": "UTC",

        })


    content = await response.json()
    events = content.get("events")


    if events is None:
        return []
    return list(map(EventResponse.parse_obj, events))


@bot.command(
    name="my_first_command",
    description="This is the first command I made!",
    scope=854512743553826906,
)
async def my_first_command(ctx: interactions.CommandContext):
    await ctx.send("Hi there!")

@bot.command(
    name="events",
    description="list of all the events",
    scope=854512743553826906,
)


async def events(ctx:interactions.CommandContext):
    display = ''
    for event in await list_events():
        display += F'{event.start_dt}, {event.end_dt}, {event.title}'
    await ctx.send(display)

bot.start()
