from discord import TextChannel, RawReactionActionEvent
from discord.ext import tasks
from discord.ext.commands import Bot, Cog
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from bot.logger import get as get_logger
from common.database import get_db, Panel, Reaction
from .helpers import get_channel_category
from .tickets import create_ticket


class ReactionPanels(Cog):
    def __init__(self, bot: Bot):
        self.logger = get_logger("extensions.ticketing.panels")
        self.bot = bot

        # Start the reactions task
        self.ensure_initial_reactions.start()

        self.logger.info("loaded ticketing reaction panels")

    def cog_unload(self):
        # Stop the reactions task
        self.ensure_initial_reactions.cancel()

        self.logger.info("unloaded ticketing reaction panels")

    @Cog.listener()
    async def on_raw_reaction_add(self, event: RawReactionActionEvent):
        assert event.member is not None

        # Ignore any bot reactions
        if event.member.bot:
            return

        # Remove the user's reaction, regardless as to whether it is valid
        channel = await self.bot.fetch_channel(event.channel_id)
        message = await channel.fetch_message(event.message_id)
        await message.remove_reaction(event.emoji, event.member)

        guild = channel.guild

        async with get_db() as db:
            # Ensure it is a reaction to a channel
            result = await db.execute(
                select(Panel).where(Panel.message_id == event.message_id)
            )
            panel = result.scalars().first()
            if panel is None:
                return

            # Ensure the reaction is one of the pre-determined ones
            result = await db.execute(
                select(Reaction)
                .where(Reaction.emoji == str(event.emoji))
                .where(Reaction.panel_id == panel.id)
            )
            reaction = result.scalars().first()
            if reaction is None:
                return

            # Get the channel category
            category = await get_channel_category(guild.categories)
            if category is None:
                return

        # Create the new ticket
        await create_ticket(
            creator=event.member,
            channel_category=category,
            guild=guild,
            category_id=reaction.category_id,
            reason=None,
        )

    @tasks.loop(minutes=30)
    async def ensure_initial_reactions(self):
        """
        Ensure that the panels have reactions send by the bot
        """
        await self.bot.wait_until_ready()

        # Get all the panels with their reactions
        async with get_db() as db:
            statement = select(Panel).options(selectinload(Panel.reactions))
            result = await db.execute(statement)
            panels = result.scalars().all()

        for panel in panels:
            # Get the channel parent channel
            channel = await self.bot.fetch_channel(panel.channel_id)
            if channel is None:
                continue

            # Get the message in the channel
            message = await channel.fetch_message(panel.message_id)
            if message is None:
                continue

            # Add all the panel reactions
            for reaction in panel.reactions:
                await message.add_reaction(reaction.emoji)
