from discord.ext.commands import check, Context
from sqlalchemy.future import select

from common.database import get_db, Setting, SettingsKey, Ticket


def in_ticket():
    """
    Require that the command is executed within the context of a ticket
    """

    async def predicate(ctx: Context):
        # Find the category a ticket could be in
        async with get_db() as db:
            statement = select(Setting).where(Setting.key == SettingsKey.TicketCategory)
            result = await db.execute(statement)
        category = result.scalars().first()
        category_id = int(category.value)

        # Check that the channel is in a proper category
        if ctx.channel.category is not None and ctx.channel.category.id != category_id:
            return False

        # Check that the channel is a ticket
        async with get_db() as db:
            statement = select(Ticket).where(Ticket.channel_id == ctx.channel.id)
            result = await db.execute(statement)
            if result.scalars().first() is None:
                return

        return True

    return check(predicate)
