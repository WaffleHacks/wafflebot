from discord.ext.commands import check, Context

from common import REDIS, Key


def has_role(*keys: Key):
    """
    Require the executor to have certain role
    :param keys: the roles to query for
    """

    async def predicate(ctx: Context):
        # Find the roles that are required to use the command
        result = await REDIS.kv.get_multiple(*keys)
        required_roles = set(result)

        # Find all roles for a user
        roles = set(map(lambda r: r.id, ctx.author.roles))

        # Check the intersection
        return len(required_roles & roles) != 0

    return check(predicate)
