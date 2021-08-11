from aiohttp import ClientSession
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse, Response, URL
from typing import Dict, Optional

from common import SETTINGS
from common.constants import MANAGE_SERVER_PERMISSIONS
from common.database import get_db, User
from .models import UserInfo
from .oauth import get_discord_client
from ..utils.session import get_session, is_logged_in, Session

router = APIRouter()


@router.get("/login")
async def login(request: Request):
    """
    Initiate the OAuth2 login flow
    """
    client = get_discord_client()
    return await client.authorize_redirect(request, request.url_for("callback"))


@router.get("/callback")
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

    # Get the authorization token
    if code:
        token = await client.authorize_access_token(request)
    else:
        return RedirectResponse(URL("/login").include_query_params(error=error))

    # Get the user's info
    client.token = token
    user_info = await client.userinfo(token=token)

    # Get all the user's guilds
    async with ClientSession() as session:
        async with session.get(
            "https://discord.com/api/v8/users/@me/guilds",
            headers={"Authorization": f"Bearer {token['access_token']}"},
        ) as response:
            guilds = await response.json()

    # Determine if the user has panel
    # TODO: change to role based permissions
    has_panel = False
    for guild in guilds:
        # Get the field
        gid = guild.get("id")
        is_owner = guild.get("owner")
        permissions = int(guild.get("permissions"))

        # Ignore servers that don't match the expected id
        if gid != str(SETTINGS.api.guild_id):
            continue

        # Set the panel
        has_panel = (
            is_owner
            or permissions & MANAGE_SERVER_PERMISSIONS == MANAGE_SERVER_PERMISSIONS
        )

    # Save the user's info to the database
    user = User(
        id=int(user_info["id"]),
        username=user_info["username"],
        avatar=user_info["picture"],
        has_panel=has_panel,
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
    request.session["token"] = dict(token)
    request.session["has_panel"] = has_panel

    return RedirectResponse("/login/complete")


@router.get("/logout", status_code=204)
async def logout(session=Depends(get_session)):
    """
    Logout out a user
    """
    # Remove everything from their session
    session.pop("user", None)
    session.pop("token", None)
    session["logged_in"] = False

    return Response(status_code=204)


@router.get("/me", response_model=UserInfo)
async def me(
    _=Depends(is_logged_in),
    user: Dict = Depends(Session("user")),
    expiration: int = Depends(Session("token.expires_at")),
):
    """
    Retrieve the currently logged in user's profile
    """
    user["expiration"] = expiration
    return user
