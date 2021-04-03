from discord.ext.commands import check, Context


def in_ticket():
    """
    Require that the command is executed within the context of a ticket
    """

    async def predicate(ctx: Context):
        # Check that the channel is a ticket
        # TODO: get category(s) from database
        if ctx.channel.category.name != "Tickets":
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
