from datetime import datetime
from discord import Member
from discord.ext.commands import Bot, Cog, command, Context

from ..converters import DateTimeConverter
from ..logger import get as get_logger

DESCRIPTION = "Open and manage support tickets"

# TODO: add commands for claim, transfer, and unclaim
# claim    -> assigns a staff member to a ticket         (staff)
# transfer -> transfers a claimed ticket to another user (staff)
# unclaim  -> removes the claim on the current ticket    (staff)


class Ticketing(Cog):
    def __init__(self, bot: Bot):
        self.logger = get_logger("extensions.ticketing")
        self.bot = bot

        self.logger.info("loaded ticketing commands")

    def cog_unload(self):
        self.logger.info("unloaded ticketing commands")

    @command()
    async def add(self, ctx: Context, user: Member):
        """
        Add a user to the current ticket
        :param ctx: the command context
        :param user: the user to add
        """
        pass

    @command()
    async def close(self, ctx: Context, *, at: DateTimeConverter = datetime.utcnow()):
        """
        Close the current ticket. Can be delayed with the `at` argument, defaults to now.
        :param ctx: the command context
        :param at: when to close the ticket
        """
        pass

    @command()
    async def open(self, ctx: Context, reason: str = ""):
        """
        Open a new ticket
        :param ctx: the command context
        :param reason: an optional reason for why
        """
        pass

    @command()
    async def panel(self, ctx: Context):
        """
        Get a link to the panel
        :param ctx: the command context
        """
        pass

    @command()
    async def remove(self, ctx: Context, user: Member):
        """
        Remove a user from the current ticket
        :param ctx: the command context
        :param user: the user to remove
        """
        pass

    @command()
    async def rename(self, ctx: Context, name: str):
        """
        Rename the current ticket
        :param ctx: the command context
        :param name: the ticket's new name
        """
        pass

    @command()
    async def sync(self, ctx: Context):
        """
        Sync the bot's database to the channels
        :param ctx: the command context
        """
        pass


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
