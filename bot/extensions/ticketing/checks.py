from discord.ext.commands import check, Context
from sqlalchemy.future import select

from common.database import get_db, Setting, SettingsKey


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

        # Check that the channel has the proper name format
        # TODO: the ticket id in the database should probably correspond to the channel id in Discord
        try:
            parts = ctx.channel.name.split("-")
            if len(parts) != 2:
                return False

            int(parts[1])
        except ValueError:
            return False

        return True

    return check(predicate)
