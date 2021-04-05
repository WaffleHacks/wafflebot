from discord import Embed, TextChannel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from common.constants import EMBED_COLOR
from common.database import get_db, Panel, Reaction
from .models import GenericPanel, PanelIn, PanelUpdate, SpecificPanel
from .reactions import router as reactions_router
from .utils import validate_emoji
from ..utils.client import with_discord, Client

router = APIRouter()
router.include_router(reactions_router, tags=["panels", "reactions"])


@router.get("/", response_model=List[GenericPanel])
async def list_panels(db: AsyncSession = Depends(get_db)):
    statement = select(Panel)
    result = await db.execute(statement)
    return result.scalars().all()


@router.post("/", response_model=GenericPanel)
async def create(
    fields: PanelIn,
    db: AsyncSession = Depends(get_db),
    discord: Client = Depends(with_discord),
):
    # Construct the model
    panel = Panel(
        title=fields.title, content=fields.content, channel_id=fields.channel_id
    )

    # Get the specified channel
    channel = await discord.fetch_channel(panel.channel_id)
    if channel is None:
        raise HTTPException(status_code=400, detail="could not find specified channel")
    elif not isinstance(channel, TextChannel):
        raise HTTPException(status_code=400, detail="channel must be a text channel")

    # Check that the emojis exist
    for reaction in fields.reactions:
        # Ensure the emoji is valid
        emoji = await validate_emoji(channel, reaction.emoji)

        # Add the reaction to the panel
        panel.reactions.append(
            Reaction(category_id=reaction.category_id, emoji=str(emoji))
        )

    # Build and send the message
    message = await channel.send(
        embed=Embed(
            title=panel.title, description=panel.content, type="rich", color=EMBED_COLOR
        )
    )
    panel.message_id = message.id

    # Add the reactions
    for reaction in panel.reactions:
        await message.add_reaction(reaction.emoji)

    # Add it to the database
    async with db.begin():
        db.add(panel)

    return panel


@router.get("/{primary_key}", response_model=SpecificPanel)
async def read(
    primary_key: int,
    db: AsyncSession = Depends(get_db),
    discord: Client = Depends(with_discord),
):
    # Get the panel and the reactions
    statement = (
        select(Panel)
        .where(Panel.id == primary_key)
        .options(selectinload(Panel.reactions))
        .options(selectinload(Panel.reactions, Reaction.category))
    )
    result = await db.execute(statement)
    panel = result.scalars().first()
    if panel is None:
        raise HTTPException(status_code=404, detail="not found")

    # Get the channel name from the id
    channel = await discord.fetch_channel(panel.channel_id)
    channel_name = channel.name if channel is not None else "<DNE>"

    return SpecificPanel(
        id=panel.id,
        title=panel.title,
        content=panel.content,
        channel=channel_name,
        reactions=panel.reactions,
    )


@router.put("/{primary_key}", response_model=GenericPanel)
async def update(
    primary_key: int,
    fields: PanelUpdate,
    db: AsyncSession = Depends(get_db),
    discord: Client = Depends(with_discord),
):
    # Get the panel
    panel = await db.get(Panel, primary_key)
    if panel is None:
        raise HTTPException(status_code=404, detail="not found")

    # Set the fields
    if fields.title is not None:
        panel.title = fields.title
    if fields.content is not None:
        panel.content = fields.content
    if fields.channel_id is not None:
        # Get the old channel
        old_channel = await discord.fetch_channel(panel.channel_id)
        if old_channel is not None:
            # Delete the old message
            old_message = await old_channel.fetch_message(panel.message_id)
            if old_message is not None:
                await old_message.delete()

        # Get the specified channel
        channel = await discord.fetch_channel(fields.channel_id)
        if channel is None:
            raise HTTPException(
                status_code=400, detail="could not find specified channel"
            )
        elif not isinstance(channel, TextChannel):
            raise HTTPException(
                status_code=400, detail="channel must be a text channel"
            )

        # Rebuild and send the message
        message = await channel.send(
            embed=Embed(
                title=panel.title,
                description=panel.content,
                type="rich",
                color=EMBED_COLOR,
            )
        )

        # Add reactions to the message
        for reaction in panel.reactions:
            await message.add_reaction(reaction)

        # Save the ids
        panel.message_id = message.id
        panel.channel_id = fields.channel_id

    # Commit the changes
    db.add(panel)
    await db.commit()

    # Update the message if the title or content was updated but not the channel
    if (
        fields.title is not None or fields.content is not None
    ) and fields.channel_id is None:
        # Fetch the channel
        channel = await discord.fetch_channel(panel.channel_id)
        if channel is not None:
            assert isinstance(channel, TextChannel)

            # Fetch the message
            message = await channel.fetch_message(panel.message_id)
            if message is not None:
                # Update the embed
                embed = Embed(
                    color=EMBED_COLOR, title=panel.title, description=panel.content
                )
                await message.edit(embed=embed)

    return panel


@router.delete("/{primary_key}")
async def delete(
    primary_key: int,
    db: AsyncSession = Depends(get_db),
    discord: Client = Depends(with_discord),
):
    # Get the panel
    panel = await db.get(Panel, primary_key)

    # Delete it if it exists
    if panel is not None:
        # Delete the message
        channel = await discord.fetch_channel(panel.channel_id)
        assert isinstance(channel, TextChannel)
        if channel is not None:
            message = await channel.fetch_message(panel.message_id)
            if message is not None:
                await message.delete()

        await db.delete(panel)
        await db.commit()

    return {"success": True}
