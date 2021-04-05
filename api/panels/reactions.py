from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from common.database import get_db, Category, Panel, Reaction
from .models import Reaction as ReactionResponse, ReactionIn, ReactionUpdate
from .utils import validate_emoji
from ..utils.client import get_channel

router = APIRouter(prefix="/{panel_id}/reactions")


async def get_panel(db: AsyncSession, id_: int, with_reactions=False) -> Panel:
    """
    Get the panel by its ID
    :param db: a database session
    :param id_: the panel's primary key
    :param with_reactions: whether to include reactions
    """
    # Construct the select statement
    statement = select(Panel).where(Panel.id == id_)
    if with_reactions:
        statement.options(selectinload(Panel.reactions))

    # Fetch the panel
    result = await db.execute(statement)
    panel = result.scalars().first()
    if panel is None:
        raise HTTPException(status_code=404, detail="not found")

    return panel


@router.get("/", response_model=List[ReactionResponse])
async def list_reactions(panel_id: int, db: AsyncSession = Depends(get_db)):
    # Ensure the panel exists
    await get_panel(db, panel_id)

    # Get all the panel's reactions
    statement = (
        select(Reaction)
        .where(Reaction.panel_id == panel_id)
        .options(selectinload(Reaction.category))
    )
    result = await db.execute(statement)
    return result.scalars().all()


@router.post("/", response_model=ReactionResponse)
async def add(
    panel_id: int,
    fields: ReactionIn,
    db: AsyncSession = Depends(get_db),
):
    # Ensure the panel exists
    panel = await get_panel(db, panel_id)

    # If the emoji is custom, check that it exists
    channel = await get_channel(panel.channel_id)
    emoji = await validate_emoji(channel, fields.emoji)

    # Add the reaction to the panel
    try:
        reaction = Reaction(
            category_id=fields.category_id, emoji=emoji, panel_id=panel_id
        )
        db.add(reaction)
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="specified category does not exist")

    # Re-fetch reaction to add the category
    statement = (
        select(Reaction)
        .where(Reaction.id == reaction.id)
        .options(selectinload(Reaction.category))
    )
    reaction = (await db.execute(statement)).scalars().first()

    # React with the emoji on the message
    channel = await get_channel(panel.channel_id)
    message = await channel.fetch_message(panel.message_id)
    if message is not None:
        await message.add_reaction(emoji)

    return reaction


@router.put("/{primary_key}", response_model=ReactionResponse)
async def update(
    panel_id: int,
    primary_key: int,
    fields: ReactionUpdate,
    db: AsyncSession = Depends(get_db),
):
    # Fetch the panel
    panel = await get_panel(db, panel_id)

    # Fetch the reaction
    statement = (
        select(Reaction)
        .where(Reaction.id == primary_key)
        .where(Reaction.panel_id == panel_id)
        .options(selectinload(Reaction.category))
    )
    result = await db.execute(statement)
    reaction = result.scalars().first()
    if reaction is None:
        raise HTTPException(status_code=404, detail="not found")

    # Update fields
    if fields.category_id is not None:
        # Check that the category exists
        if await db.get(Category, fields.category_id) is None:
            raise HTTPException(status_code=400, detail="category does not exist")

        reaction.category_id = fields.category_id
    if fields.emoji is not None:
        # Get the channel
        channel = await get_channel(panel.channel_id)

        # If the emoji is custom, check that it exists
        emoji = await validate_emoji(channel, fields.emoji)

        # Update the reaction
        message = await channel.fetch_message(panel.message_id)
        if message is not None:
            await message.remove_reaction(reaction.emoji, message.author)
            await message.add_reaction(emoji)

        reaction.emoji = emoji

    # Commit the changes
    db.add(reaction)
    await db.commit()
    await db.refresh(reaction)

    return reaction


@router.delete("/{primary_key}")
async def remove(panel_id: int, primary_key: int, db: AsyncSession = Depends(get_db)):
    # Fetch the panel
    panel = await get_panel(db, panel_id)

    # Fetch the reaction
    statement = (
        select(Reaction)
        .where(Reaction.id == primary_key)
        .where(Reaction.panel_id == panel_id)
    )
    result = await db.execute(statement)
    reaction = result.scalars().first()
    if reaction is not None:
        # Get the message for the panel
        channel = await get_channel(panel.channel_id)
        message = await channel.fetch_message(panel.message_id)

        # Remove the reaction
        if message is not None:
            await message.remove_reaction(reaction.emoji, message.author)

        # Delete the reaction from the database
        await db.delete(reaction)

    return {"success": True}
