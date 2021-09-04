from discord.ext.commands import check, Context
from sentry_sdk import start_transaction

from common import CONFIG, ConfigKey


def has_role(*keys: ConfigKey):
    """
    Require the executor to have certain role
    :param keys: the roles to query for
    """

    async def predicate(ctx: Context):
        with start_transaction(name="permissions", op="has_role"):
            # Find the roles that are required to use the command
            result = await CONFIG.get_multiple(*keys)
            required_roles = set(result)

            # Find all roles for a user
            roles = set(map(lambda r: r.id, ctx.author.roles))

            # Check the intersection
            return len(required_roles & roles) != 0

    return check(predicate)
