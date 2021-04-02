import dateparser
from datetime import datetime
from discord.ext.commands import BadArgument, Context, Converter


class DateTimeConverter(Converter):
    async def convert(self, ctx: Context, argument: str) -> datetime:
        # Parse the timezone in UTC
        parsed = dateparser.parse(argument, settings={"TO_TIMEZONE": "UTC"})

        # Throw error if could not parse
        if parsed is None:
            raise BadArgument("invalid date/time format")

        return parsed
