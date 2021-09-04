from discord import Object
from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sentry_sdk import start_span
from typing import Optional, Union

from common import CONFIG, SETTINGS
from common.observability import with_transaction
from .models import Webhook, TestingWebhook
from ..utils.client import with_discord


def is_allowed(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="unauthorized")

    if authorization.replace("Bearer ", "") != SETTINGS.api.webhook_secret:
        raise HTTPException(status_code=401, detail="unauthorized")


router = APIRouter(dependencies=[Depends(is_allowed)])


@router.post("/hackathon-manager", response_model=None, status_code=204)
@with_transaction("webhooks.discord_username_changed")
async def discord_username_changed(
    body: Union[TestingWebhook, Webhook], discord=Depends(with_discord)
):
    if body.type == "testing":
        return Response(status_code=204)

    with start_span(op="fetch_guild"):
        guild = await discord.fetch_guild(SETTINGS.discord_guild_id)

    with start_span(op="fetch_role"):
        role_id = await CONFIG.registered_role()
        role = Object(role_id)

    with start_span(op="update_member", member=body.questionnaire.discord):
        async for member in guild.fetch_members():
            if f"{member.name}#{member.discriminator}" == body.questionnaire.discord:
                await member.add_roles(role)
                break

    return Response(status_code=204)
