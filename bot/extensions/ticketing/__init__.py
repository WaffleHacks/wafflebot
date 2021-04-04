from discord.ext.commands import Bot

from .commands import Ticketing
from .panels import ReactionPanels

DESCRIPTION = "Open and manage support tickets"


def setup(bot: Bot):
    """
    Register the cog
    :param bot: the underlying bot
    """
    bot.add_cog(Ticketing(bot))
    bot.add_cog(ReactionPanels(bot))


def teardown(bot: Bot):
    """
    Unregister the cog
    :param bot: the underlying bot
    """
    bot.remove_cog("Ticketing")
    bot.remove_cog("ReactionPanels")
