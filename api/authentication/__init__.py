from aiohttp import ClientSession
from discord import Role
from fastapi import APIRouter, Depends, Query, Request
from functools import lru_cache
from sentry_sdk import start_span
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse, Response, URL
from typing import Dict, List, Optional

from common import CONFIG, SETTINGS
from common.database import get_db, User
from common.observability import with_transaction
from .models import UserInfo
from .oauth import get_discord_client
from ..utils.session import get_session, is_logged_in, Session
from ..utils.client import DISCORD

router = APIRouter()


@lru_cache(maxsize=4)
async def get_user_roles(user_id: int) -> List[Role]:
    """
    Get a user's roles from Discord
    :param user_id: the id to get roles for
    """
    guild = await DISCORD.fetch_guild(SETTINGS.discord_guild_id)
    user = await guild.fetch_member(user_id)
    return user.roles


@router.get("/login")
@with_transaction("authentication.login")
async def login(request: Request):
    """
    Initiate the OAuth2 login flow
    """
    client = get_discord_client()
    return await client.authorize_redirect(request, request.url_for("callback"))


@router.get("/callback")
@with_transaction("authentication.callback")
async def callback(
    request: Request,
    code: str = None,
    error: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Complete the OAuth2 login flow
    """
    client = get_discord_client()

    with start_span(op="oauth"):
        with start_span(op="oauth.authorization_token"):
            # Get the authorization token
            if code:
                token = await client.authorize_access_token(request)
            else:
                return RedirectResponse(URL("/login").include_query_params(error=error))

        with start_span(op="oauth.user_info"):
            # Get the user's info
            client.token = token
            user_info = await client.userinfo(token=token)
            user_id = int(user_info.get("id"))

    with start_span(op="permissions"):
        with start_span(op="permissions.access"):
            # Get the user's role ids
            roles = list(map(lambda r: r.id, await get_user_roles(user_id)))

            # Determine if the user has panel access
            if (await CONFIG.panel_access_role()) not in roles:
                return RedirectResponse("/login?error=unauthorized")

        with start_span(op="permissions.admin"):
            # Get all the user's guilds
            async with ClientSession() as session:
                async with session.get(
                    "https://discord.com/api/v8/users/@me/guilds",
                    headers={"Authorization": f"Bearer {token['access_token']}"},
                ) as response:
                    guilds = await response.json()

            # Determine if the user has admin access
            is_owner = any(
                map(
                    lambda g: g.get("id") == str(SETTINGS.discord_guild_id)
                    and g.get("owner"),
                    guilds,
                )
            )
            is_admin = (await CONFIG.management_role()) in roles or is_owner

    # Save the user's info to the database
    user = User(
        id=user_id,
        username=user_info["username"],
        avatar=user_info["picture"],
        is_admin=is_admin,
    )

    # Insert and ignore failures
    try:
        db.add(user)
        await db.commit()
    except IntegrityError:
        pass

    # Store the info in the session
    request.session["logged_in"] = True
    request.session["user"] = dict(user_info)
    request.session["is_admin"] = is_admin
    request.session["expiration"] = dict(token).get("expires_at")

    return RedirectResponse("/login/complete")


@router.get("/logout", status_code=204)
@with_transaction("authentication.logout")
async def logout(session=Depends(get_session)):
    """
    Logout out a user
    """
    # Remove everything from their session
    for key in list(session):
        del session[key]
    session["logged_in"] = False

    return Response(status_code=204)


@router.get("/me", response_model=UserInfo)
@with_transaction("authentication.me")
async def me(
    _=Depends(is_logged_in),
    user: Dict = Depends(Session("user")),
    expiration: int = Depends(Session("expiration")),
    is_admin: bool = Depends(Session("is_admin")),
):
    """
    Retrieve the currently logged in user's profile
    """
    user["expiration"] = expiration
    user["is_admin"] = is_admin
    return user
