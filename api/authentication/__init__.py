from fastapi import APIRouter, Depends, Query, Request
from starlette.responses import RedirectResponse, Response, URL
from typing import Dict, Optional

from ..utils.session import get_session, is_logged_in, Session
from .models import UserInfo
from .oauth import get_discord_client

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

    # Store the info in the session
    request.session["logged_in"] = True
    request.session["user"] = dict(user_info)
    request.session["token"] = dict(token)

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
