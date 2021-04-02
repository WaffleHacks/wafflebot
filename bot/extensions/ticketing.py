import asyncio
from datetime import datetime
from discord import utils, TextChannel, Member, PermissionOverwrite
from discord.ext.commands import Bot, Cog, command, Context
from sqlalchemy.exc import IntegrityError
from typing import Optional

from common.database import get_db, SettingsKey, Ticket, User
from .. import embeds
from ..converters import DateTimeConverter
from ..logger import get as get_logger
from ..permissions import has_role

DESCRIPTION = "Open and manage support tickets"

# TODO: add commands for claim, transfer, and unclaim
# claim    -> assigns a staff member to a ticket         (staff)
# transfer -> transfers a claimed ticket to another user (staff)
# unclaim  -> removes the claim on the current ticket    (staff)


async def close_ticket(ticket_id: int, channel: TextChannel, wait: int):
    """
    Close a ticket and remove its channel
    :param ticket_id: the id of the ticket
    :param channel: the discord channel
    :param wait: the number of seconds to wait before deleting
    """
    # Wait before deleting the ticket
    await asyncio.sleep(wait)

    async with get_db() as db:
        # Retrieve the ticket from the database
        ticket = await db.get(Ticket, ticket_id)
        if ticket is None:
            return

        # Mark the ticket as closed
        ticket.is_open = False
        await db.commit()

    # Delete the channel
    await channel.delete()


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
    @has_role(SettingsKey.MentionRole)
    async def close(self, ctx: Context, *, at: Optional[DateTimeConverter]):
        """
        Close the current ticket. Can be delayed with the `at` argument, defaults to now.
        :param ctx: the command context
        :param at: when to close the ticket
        """
        # Check that the channel is a ticket
        # TODO: get category(s) from database
        if ctx.channel.category.name != "Tickets":
            return

        # Retrieve the ticket id from the channel name
        # TODO: the ticket id in the database should probably correspond to the channel id in Discord
        try:
            parts = ctx.channel.name.split("-")
            if len(parts) != 2:
                return

            ticket_id = int(parts[1])
        except ValueError:
            return

        # Close the ticket
        if at is None:
            await close_ticket(ticket_id, ctx.channel, 0)
        else:
            # Calculate the seconds to wait
            delta = at - datetime.utcnow()
            seconds = delta.total_seconds()

            # Ensure the time to wait is positive
            if seconds < 0:
                await ctx.channel.send("Cannot close channel in the past!")
                return

            self.bot.loop.create_task(close_ticket(ticket_id, ctx.channel, seconds))

    @command(aliases=["ticket"])
    async def open(self, ctx: Context, *, reason: str = ""):
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
        embed = embeds.default(ctx.author)
        embed.description = f":white_check_mark: Your ticket has been created!\n\n{ticket_channel.mention}"
        await ctx.channel.send(embed=embed)

        # Ping the people for the ticket and instantly delete the message
        ping_message = " ".join(
            [entity.mention for entity in authorized if entity is not None]
        )
        ping = await ticket_channel.send(ping_message)
        await ping.delete()

        # Create the "welcome" embed
        # TODO: get embed content from DB
        embed = embeds.default(ctx.author, has_footer=False)
        embed.title = "New Ticket"
        await ticket_channel.send(embed=embed)

    @command()
    async def panel(self, ctx: Context):
        """
        Get a link to the panel
        :param ctx: the command context
        """
        embed = embeds.default(ctx.author)
        embed.title = "Panel"
        embed.description = (
            "Here's the link to the [panel](https://bot.wafflehacks.tech/)"
        )
        await ctx.channel.send(embed=embed)

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
