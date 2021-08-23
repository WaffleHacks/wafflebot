from discord import Object
from fastapi import APIRouter, Depends, Response

from common import CONFIG, SETTINGS
from .models import UpdateDiscord
from ..utils.client import with_discord

router = APIRouter()


@router.post("/hackathon-manager/discord", response_model=None, status_code=204)
async def discord_update(body: UpdateDiscord, discord=Depends(with_discord)):
    guild = await discord.fetch_guild(SETTINGS.discord_guild_id)

    role_id = await CONFIG.registered_role()
    role = Object(role_id)

    async for member in guild.fetch_members():
        if f"{member.name}#{member.discriminator}" == body.questionnaire.discord:
            await member.add_roles(role)
            break

    return Response(status_code=204)
