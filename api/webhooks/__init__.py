from discord import Object
from fastapi import APIRouter, Depends, Header, HTTPException, Response
from typing import Optional, Union

from common import CONFIG, SETTINGS
from .models import Webhook, TestingWebhook
from ..utils.client import with_discord


def is_allowed(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="unauthorized")

    if authorization.replace("Bearer ", "") != SETTINGS.api.webhook_secret:
        raise HTTPException(status_code=401, detail="unauthorized")


router = APIRouter(dependencies=[Depends(is_allowed)])


@router.post("/hackathon-manager", response_model=None, status_code=204)
async def discord_username_changed(
    body: Union[TestingWebhook, Webhook], discord=Depends(with_discord)
):
    if body.type == "testing":
        return Response(status_code=204)

    guild = await discord.fetch_guild(SETTINGS.discord_guild_id)

    role_id = await CONFIG.registered_role()
    role = Object(role_id)

    async for member in guild.fetch_members():
        if f"{member.name}#{member.discriminator}" == body.questionnaire.discord:
            await member.add_roles(role)
            break

    return Response(status_code=204)
