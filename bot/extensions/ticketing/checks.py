from discord.ext.commands import check, Context
from sqlalchemy.future import select

from common.database import get_db, Ticket
from .helpers import get_channel_category


def in_ticket():
    """
    Require that the command is executed within the context of a ticket
    """

    async def predicate(ctx: Context):
        # Check that the channel is in the proper category
        if ctx.channel.category is None:
            return
        category = await get_channel_category(ctx.guild.categories)
        if category.id != ctx.channel.category.id:
            return False

        # Check that the channel is a ticket
        async with get_db() as db:
            statement = select(Ticket).where(Ticket.channel_id == ctx.channel.id)
            result = await db.execute(statement)
            if result.scalars().first() is None:
                return False

        return True

    return check(predicate)
