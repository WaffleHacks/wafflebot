from discord.ext.commands import Bot

from .commands import Ticketing

DESCRIPTION = "Open and manage support tickets"


def setup(bot: Bot):
    """
    Register the cog
    :param bot: the underlying bot
    """
    bot.add_cog(Ticketing(bot))


def teardown(bot: Bot):
    """
    Unregister the cog
    :param bot: the underlying bot
    """
    bot.remove_cog("Ticketing")
