import aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from websockets.exceptions import ConnectionClosed

from common import SETTINGS
from common.database import get_db, Category, Message, Ticket
from .categories import router as categories_router
from .models.tickets import TicketMessage, TicketResponse, TicketUpdate

router = APIRouter()
router.include_router(
    categories_router, prefix="/categories", tags=["tickets", "categories"]
)


@router.get("/", response_model=List[TicketResponse])
async def list_tickets(
    category: Optional[int] = None, db: AsyncSession = Depends(get_db)
):
    statement = select(Ticket).where(Ticket.category_id == category)
    result = await db.execute(statement)
    return result.scalars().all()


@router.put("/{primary_key}", response_model=TicketResponse)
async def update(
    primary_key: int, fields: TicketUpdate, db: AsyncSession = Depends(get_db)
):
    # Find the ticket
    ticket = await db.get(Ticket, primary_key)
    if ticket is None:
        raise HTTPException(status_code=404, detail="not found")

    # Set the fields
    if fields.reason is not None:
        ticket.reason = fields.reason
    if fields.category_id is not None:
        category = await db.get(Category, fields.category_id)
        if category is None:
            raise HTTPException(status_code=400, detail="category not found")

        ticket.category_id = category.id

    # Commit the changes
    db.add(ticket)
    await db.commit()

    return ticket


# TODO: restrict to admins (requires permission system)
@router.delete("/{primary_key}")
async def delete(primary_key: int, db: AsyncSession = Depends(get_db)):
    # Get the ticket
    ticket = await db.get(Ticket, primary_key)

    # Delete it if it exists
    if ticket is not None:
        await db.delete(ticket)
        await db.commit()

    return {"success": True}


@router.get("/{primary_key}/messages", response_model=List[TicketMessage])
async def messages(primary_key: int, db: AsyncSession = Depends(get_db)):
    # Get the ticket
    statement = (
        select(Ticket)
        .where(Ticket.id == primary_key)
        .options(selectinload(Ticket.messages))
        .options(selectinload(Ticket.messages, Message.sender))
    )
    result = await db.execute(statement)
    ticket = result.scalars().first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="not found")

    return ticket.messages


@router.websocket("/{primary_key}/messages/ws")
async def messages_stream(
    ws: WebSocket, primary_key: int, db: AsyncSession = Depends(get_db)
):
    # Accept the connection
    await ws.accept()

    # Ensure the ticket exists
    statement = select(Ticket).where(Ticket.id == primary_key)
    result = await db.execute(statement)
    ticket = result.scalars().first()
    if ticket is None:
        await ws.send_json({"success": False, "reason": "not found", "code": 1008})
        await ws.close(1009)
        return
    elif not ticket.is_open:
        await ws.send_json({"success": False, "reason": "ticket closed", "code": 1008})
        await ws.close(1009)
        return

    # Connect to redis and subscribe to the channel
    redis = await aioredis.create_redis_pool(SETTINGS.redis_url)
    (channel,) = await redis.subscribe(f"ticket|{primary_key}")

    try:
        # Accept and re-broadcast the messages
        async for message in channel.iter(encoding="utf-8", decoder=json.loads):
            # Re-broadcast the message
            await ws.send_json(message)

            # Check if the connection should be closed
            if message.get("action") == "close":
                await ws.close(1000)
    except ConnectionClosed:
        pass

    # Disconnect from redis
    await redis.unsubscribe(channel)
    redis.close()
    await redis.wait_closed()
