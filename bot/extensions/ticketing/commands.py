from datetime import datetime
from discord import utils, Member, PermissionOverwrite
from discord.ext.commands import command, Bot, Cog, Context
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from typing import Optional

from common.database import get_db, Setting, SettingsKey, Ticket, User
from bot import embeds
from bot.converters import DateTimeConverter
from bot.logger import get as get_logger
from bot.permissions import has_role
from .checks import in_ticket
from .helpers import close_ticket, get_channel_category, get_ticket_roles

# TODO: add commands for claim, transfer, and unclaim
# claim    -> assigns a staff member to a ticket         (staff)
# transfer -> transfers a claimed ticket to another user (staff)
# unclaim  -> removes the claim on the current ticket    (staff)

TICKET_PERMISSIONS = PermissionOverwrite(
    read_messages=True,
    read_message_history=True,
    send_messages=True,
    add_reactions=True,
)


class Ticketing(Cog):
    def __init__(self, bot: Bot):
        self.logger = get_logger("extensions.ticketing")
        self.bot = bot

        self.logger.info("loaded ticketing commands")

    def cog_unload(self):
        self.logger.info("unloaded ticketing commands")

    @command()
    @has_role(SettingsKey.MentionRole, SettingsKey.PanelAccessRole)
    @in_ticket()
    async def add(self, ctx: Context, user: Member):
        """
        Add a user to the current ticket
        :param ctx: the command context
        :param user: the user to add
        """
        # Check if the user is already added
        if user in ctx.channel.overwrites:
            await ctx.channel.send(
                embed=embeds.message(
                    f":x: {user.mention} is already added to the ticket!"
                )
            )
            return

        # Set the permissions
        await ctx.channel.set_permissions(user, overwrite=TICKET_PERMISSIONS)

        # Notify success
        await ctx.channel.send(
            embed=embeds.message(
                f":white_check_mark: Added {user.mention} to the ticket!"
            )
        )

    @command()
    @has_role(SettingsKey.MentionRole, SettingsKey.PanelAccessRole)
    @in_ticket()
    async def close(self, ctx: Context, *, at: Optional[DateTimeConverter]):
        """
        Close the current ticket. Can be delayed with the `at` argument, defaults to now.
        :param ctx: the command context
        :param at: when to close the ticket
        """
        # Check if there is an associated voice channel
        voice = utils.get(ctx.guild.voice_channels, name=ctx.channel.name)

        # Close the ticket
        if at is None:
            await close_ticket(ctx.channel, voice, 0)
        else:
            # Calculate the seconds to wait
            delta = at - datetime.utcnow()
            seconds = delta.total_seconds()

            # Ensure the time to wait is positive
            if seconds < 0:
                await ctx.channel.send("Cannot close channel in the past!")
                return

            self.bot.loop.create_task(close_ticket(ctx.channel, voice, seconds))

    @command(aliases=["ticket"])
    async def open(self, ctx: Context, *, reason: str = ""):
        """
        Open a new ticket with an optional reason
        :param ctx: the command context
        :param reason: an optional reason for why
        """
        # Get the channel category
        category = await get_channel_category(ctx.guild.categories)
        if category is None:
            await ctx.channel.send("Could not create ticket, category does not exist!")

        # Ensure the user exists in the database
        async with get_db() as db:
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

        # Create a ticket in the database
        async with get_db() as db:
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
        roles = await get_ticket_roles()
        authorized = [utils.get(ctx.guild.roles, id=int(role.value)) for role in roles]
        authorized.append(ctx.author)

        # Create text channel within category
        overwrites = {role: TICKET_PERMISSIONS for role in authorized}
        overwrites[ctx.guild.default_role] = PermissionOverwrite(view_channel=False)
        ticket_channel = await category.create_text_channel(
            f"ticket-{ticket.id}", overwrites=overwrites
        )

        # Save the channel id
        async with get_db() as db:
            ticket.channel_id = ticket_channel.id
            db.add(ticket)
            await db.commit()

        # Notify of successful creation
        await ctx.channel.send(
            embed=embeds.message(
                f":white_check_mark: Your ticket has been created!\n\n{ticket_channel.mention}"
            )
        )

        # Ping the people for the ticket and instantly delete the message
        ping_message = " ".join(
            [
                entity.mention
                for i, entity in enumerate(authorized)
                if type(entity) == Member or roles[i].key == SettingsKey.MentionRole
            ]
        )
        ping = await ticket_channel.send(ping_message)
        await ping.delete()

        # Create the "welcome" embed
        # TODO: get embed content from DB
        embed = embeds.default(ctx.author, has_footer=False)
        embed.title = "New Ticket"
        await ticket_channel.send(embed=embed)

    @command()
    @has_role(SettingsKey.PanelAccessRole)
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
    @has_role(SettingsKey.MentionRole, SettingsKey.PanelAccessRole)
    @in_ticket()
    async def remove(self, ctx: Context, user: Member):
        """
        Remove a user from the current ticket
        :param ctx: the command context
        :param user: the user to remove
        """
        # Check that the user is already in the ticket
        if user not in ctx.channel.overwrites:
            await ctx.channel.send(
                embed=embeds.message(f":x: {user.mention} is not in the ticket!")
            )
            return

        # Prevent removing support agents/managers
        roles = await get_ticket_roles()
        role_ids = set(map(lambda r: r.value, roles))
        author_roles = set(map(lambda r: str(r.id), ctx.author.roles))
        if len(role_ids & author_roles) != 0:
            await ctx.channel.send(
                embed=embeds.message(
                    f":x: Cannot remove a ticket helper or ticket manager!"
                )
            )
            return

        # Remove their permissions
        await ctx.channel.set_permissions(user, overwrite=None)

        # Notify success
        await ctx.channel.send(
            embed=embeds.message(
                f":white_check_mark: Removed {user.mention} from the ticket!"
            )
        )

    @command()
    @has_role(SettingsKey.MentionRole, SettingsKey.PanelAccessRole)
    @in_ticket()
    async def rename(self, ctx: Context, *, name: str):
        """
        Rename the current ticket
        :param ctx: the command context
        :param name: the ticket's new name
        """
        # Get the ticket's number
        number = ctx.channel.name.split("-")[-1]

        # Convert the name to a consistent format
        name = name.lower().replace(" ", "-")

        # Format the name with the number
        formatted = f"{name}{number}" if name.endswith("-") else f"{name}-{number}"

        # Rename the channel
        await ctx.channel.edit(name=formatted)

    @command()
    async def sync(self, ctx: Context):
        """
        Sync the bot's database to the channels
        :param ctx: the command context
        """
        pass

    @command()
    @has_role(SettingsKey.MentionRole, SettingsKey.PanelAccessRole)
    @in_ticket()
    async def voice(self, ctx: Context):
        """
        Create a voice channel for the ticket
        :param ctx: the command context
        """
        # Create a voice channel with the same name as the ticket
        channel = await ctx.guild.create_voice_channel(
            ctx.channel.name,
            category=ctx.channel.category,
            overwrites=ctx.channel.overwrites,
        )

        # Notify of the new channel
        await ctx.channel.send(
            embed=embeds.message(
                f":white_check_mark: Successfully create your voice channel! {channel.mention}"
            )
        )
