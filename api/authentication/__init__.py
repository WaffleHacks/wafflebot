from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

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
async def callback(request: Request, code: str = None):
    """
    Complete the OAuth2 login flow
    """
    client = get_discord_client()

    # Get the authorization token
    if code:
        token = await client.authorize_access_token(request)
    else:
        # TODO: redirect to Svelte
        return {"status": "failed"}

    # Get the user's info
    client.token = token
    user_info = await client.userinfo(token=token)

    # Store the info in the session
    request.session["logged_in"] = True
    request.session["user"] = dict(user_info)
    request.session["token"] = dict(token)

    # TODO: redirect to Svelte
    return RedirectResponse("/")


@router.get("/logout")
async def logout(request: Request):
    """
    Logout out a user
    """
    # Remove everything from their session
    request.session.pop("user", None)
    request.session.pop("token", None)
    request.session["logged_in"] = False

    return {"success": True}


@router.get("/me", response_model=UserInfo)
async def me(request: Request):
    """
    Retrieve the currently logged in user's profile
    """
    # Ensure the user is logged in
    if not request.session.get("logged_in"):
        raise HTTPException(status_code=401, detail="unauthorized")

    return request.session.get("user")
