from discord.ext.commands import check, Context
from sqlalchemy.future import select

from common.database import get_db, Setting, SettingsKey


def has_role(*keys: SettingsKey):
    """
    Require the executor to have certain role
    :param keys: the roles to query for
    """

    async def predicate(ctx: Context):
        # Find the roles that are required to use the command
        # TODO: add cache layer?
        async with get_db() as db:
            statement = select(Setting).where(Setting.key.in_(keys))
            result = await db.execute(statement)
        query_result = result.scalars().all()
        required_roles = set(map(lambda r: r.value, query_result))

        # Find all roles for a user
        roles = set(map(lambda r: str(r.id), ctx.author.roles))

        return len(required_roles & roles) != 0

    return check(predicate)
