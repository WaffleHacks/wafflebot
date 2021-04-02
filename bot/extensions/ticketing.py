from datetime import datetime
from discord import utils, Embed, Member, PermissionOverwrite, RawReactionActionEvent
from discord.ext.commands import Bot, Cog, command, Context
from sqlalchemy.exc import IntegrityError

from common.database import get_db, Ticket, User
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

    @command(aliases=["ticket"])
    async def open(self, ctx: Context, reason: str = ""):
        """
        Open a new ticket with an optional reason
        :param ctx: the command context
        :param reason: an optional reason for why
        """
        # Get the channel category
        # TODO: parameterize ticket category (discord side)
        category = utils.get(ctx.guild.categories, name="Tickets")
        if category is None:
            await ctx.channel.send("Could not create ticket, category does not exist!")

        async with get_db() as db:
            # Ensure the user exists in the database
            user = User(
                id=ctx.author.id,
                username=f"{ctx.author.name}#{ctx.author.discriminator}",
                avatar=str(ctx.author.avatar_url),
                has_panel=True,
            )
            db.add(user)

            # Save the user, ignoring any users that already exist
            try:
                await db.commit()
            except IntegrityError:
                pass

        async with get_db() as db:
            # Create a ticket in the database
            ticket = Ticket(
                # TODO: get the category for the ticket (api side)
                category_id=2,
                creator_id=user.id,
                is_open=True,
                reason=reason,
            )
            db.add(ticket)

            # Save the ticket
            await db.commit()

        # Get the role(s) that can view tickets
        # TODO: parameterize viewable authorized
        authorized = [
            utils.get(ctx.guild.roles, name="Mentor"),
            # utils.get(ctx.guild.roles, name="Organizer"),
            ctx.author,
        ]

        # Create text channel within category
        permissions = PermissionOverwrite(
            read_messages=True,
            read_message_history=True,
            send_messages=True,
            add_reactions=True,
        )
        overwrites = {role: permissions for role in authorized}
        overwrites[ctx.guild.default_role] = PermissionOverwrite(view_channel=False)
        ticket_channel = await category.create_text_channel(
            f"ticket-{ticket.id}", overwrites=overwrites
        )

        # Notify of successful creation
        await ctx.channel.send(
            embed=Embed(
                description=f":white_check_mark: Thanks for creating ticket: {ticket_channel.mention}"
            )
        )

        # Ping the people for the ticket and instantly delete the message
        ping_message = " ".join(
            [entity.mention for entity in authorized if entity is not None]
        )
        ping = await ticket_channel.send(ping_message)
        await ping.delete()

        # Create the "welcome" embed
        # TODO: get embed content from DB
        embed = Embed(title="New Ticket")
        await ticket_channel.send(embed=embed)

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
