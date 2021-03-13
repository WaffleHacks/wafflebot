from discord.ext.commands import check, Context

from common.database import Setting, SettingsKey


def has_role(key: SettingsKey):
    """
    Require the executor to have certain role
    :param key: key for the role
    """

    async def predicate(ctx: Context):
        # Find the roles that are required to use the command
        # TODO: add cache layer?
        query_result = await Setting.objects.filter(key=key).all()
        required_roles = set(map(lambda r: r.value, query_result))

        # Find all roles for a user
        roles = set(map(lambda r: str(r.id), ctx.author.roles))

        return len(required_roles & roles) != 0

    return check(predicate)
