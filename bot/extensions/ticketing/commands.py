import aioredis
from asyncio import Event
from datetime import datetime
from discord import utils, Member, Message as DiscordMessage, TextChannel
from discord.ext.commands import command, Bot, Cog, Context
from sqlalchemy import update
from sqlalchemy.future import select
from typing import Optional

from common import ConfigKey, SETTINGS
from common.database import db_context, Message, Ticket
from bot import embeds
from bot.converters import DateTimeConverter
from bot.logger import get as get_logger
from bot.permissions import has_role
from .checks import in_ticket
from .constants import TICKET_PERMISSIONS
from .helpers import create_user_if_not_exists, get_channel_category, get_ticket_roles
from .tickets import close_ticket, create_ticket

# TODO: add commands for claim, transfer, and unclaim
# claim    -> assigns a staff member to a ticket         (staff)
# transfer -> transfers a claimed ticket to another user (staff)
# unclaim  -> removes the claim on the current ticket    (staff)


class Ticketing(Cog):
    def __init__(self, bot: Bot):
        self.logger = get_logger("extensions.ticketing")
        self.bot = bot

        # Connect to redis
        self.pool: Optional[aioredis.Redis] = None
        self.pool_set = Event()
        self.bot.loop.create_task(self.__redis_connect())

        self.logger.info("loaded ticketing commands")

    def cog_unload(self):
        self.bot.loop.create_task(self.__redis_disconnect())
        self.logger.info("unloaded ticketing commands")

    async def __redis_connect(self):
        self.pool = await aioredis.create_redis_pool(SETTINGS.redis_url)
        self.pool_set.set()

    async def __redis_disconnect(self):
        self.pool.close()
        await self.pool.wait_closed()

    async def notify_action(self, name: str, action: str, **kwargs):
        """
        Notify that an action occurred
        :param name: the channel name
        :param action: the action that occurred
        """
        # Get the channel id from the name
        parts = name.split("-")
        try:
            ticket_id = int(parts[-1])
        except ValueError:
            return

        # Publish the message
        await self.pool.publish_json(
            f"ticket|{ticket_id}", {"action": action, **kwargs}
        )

    @command()
    @has_role(ConfigKey.MentionRoles, ConfigKey.PanelAccessRole)
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

        # Publish the action
        await self.notify_action(
            ctx.channel.name,
            "add",
            user=f"{ctx.author.name}#{ctx.author.discriminator}",
        )

    @command()
    @has_role(ConfigKey.MentionRoles, ConfigKey.PanelAccessRole)
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
            await close_ticket(ctx.author.id, ctx.channel, voice, 0, self.pool)
        else:
            # Calculate the seconds to wait
            delta = at - datetime.utcnow()
            seconds = delta.total_seconds()

            # Ensure the time to wait is positive
            if seconds < 0:
                await ctx.channel.send("Cannot close channel in the past!")
                return

            # TODO: add persistence for timed closing
            self.bot.loop.create_task(
                close_ticket(ctx.author.id, ctx.channel, voice, seconds, self.pool)
            )

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
            self.logger.error("could not create ticket, category does not exist")
            return

        ticket, ticket_channel = await create_ticket(
            creator=ctx.author,
            channel_category=category,
            guild=ctx.guild,
            category_id=None,
            reason=reason,
        )

        # Notify of successful creation
        await ctx.channel.send(
            embed=embeds.message(
                f":white_check_mark: Your ticket has been created!\n\n{ticket_channel.mention}"
            )
        )

    @command()
    @has_role(ConfigKey.PanelAccessRole)
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
    @has_role(ConfigKey.MentionRoles, ConfigKey.PanelAccessRole)
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
        role_ids = set(await get_ticket_roles())
        author_roles = set(map(lambda r: r.id, ctx.author.roles))
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

        # Publish the action
        await self.notify_action(
            ctx.channel.name,
            "remove",
            user=f"{ctx.author.name}#{ctx.author.discriminator}",
        )

    @command()
    @has_role(ConfigKey.MentionRoles, ConfigKey.PanelAccessRole)
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

        # Publish the action
        await self.notify_action(ctx.channel.name, "rename", new_name=formatted)

    @command()
    @has_role(ConfigKey.PanelAccessRole)
    async def sync(self, ctx: Context):
        """
        Sync the discord channels with the bot's database
        :param ctx: the command context
        """
        # Get the channel category
        category = await get_channel_category(ctx.guild.categories)
        if category is None:
            return

        # Get all the channel ids
        channel_ids = [channel.id for channel in category.channels]

        # Mark all tickets as closed that no longer have their channel
        async with db_context() as db:
            statement = (
                update(Ticket)
                .where(Ticket.is_open.is_(True), Ticket.channel_id.not_in(channel_ids))
                .values(is_open=False)
            )
            result = await db.execute(statement)
            await db.commit()

        # Notify success
        if result.rowcount == 0:
            message = embeds.message(
                ":white_check_mark: The database is already in sync!"
            )
        else:
            message = embeds.message(
                f":white_check_mark: {result.rowcount} tickets marked as closed!"
            )
        await ctx.channel.send(embed=message)

    @command()
    @has_role(ConfigKey.MentionRoles, ConfigKey.PanelAccessRole)
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
                f":white_check_mark: Successfully create your voice channel! <#{channel.id}>"
            )
        )

        # Publish the action
        await self.notify_action(ctx.channel.name, "voice")

    @Cog.listener()
    async def on_message(self, message: DiscordMessage):
        # Wait until redis is defined
        await self.pool_set.wait()

        # Ignore the message if it doesn't have content
        if message.content == "":
            return

        # Only work for text channels
        if not isinstance(message.channel, TextChannel):
            return

        # Ignore messages not in a category
        if message.channel.category is None:
            return

        # Check if channel is in the ticket category
        category = await get_channel_category(message.guild.categories)
        if category.id != message.channel.category_id:
            return

        # Ensure the user exists
        await create_user_if_not_exists(message.author)

        async with db_context() as db:
            # Check that the channel is a ticket
            statement = select(Ticket).where(Ticket.channel_id == message.channel.id)
            result = await db.execute(statement)
            ticket = result.scalars().first()
            if ticket is None:
                return

            # Create the new message
            msg = Message(
                ticket=ticket,
                sender_id=message.author.id,
                content=message.content,
            )
            db.add(msg)

            # Save the changes
            await db.commit()

        # Notify of the new message
        await self.pool.publish_json(
            f"ticket|{ticket.id}",
            {
                "author": f"{message.author.name}#{message.author.discriminator}",
                "avatar": str(message.author.avatar_url),
                "message": message.content,
            },
        )
