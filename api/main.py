from fastapi import Depends, FastAPI, Request
from fastapi.responses import UJSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from common import SETTINGS
from .authentication import router as authentication_router
from .canned_responses import router as canned_responses_router
from .panels import router as panel_router
from .tickets import router as tickets_router
from .static import router as static_router
from .utils.client import DISCORD
from .utils.session import is_logged_in

app = FastAPI(docs_url=None, swagger_ui_oauth2_redirect_url=None, redoc_url="/docs")

# Register middleware
app.add_middleware(SessionMiddleware, secret_key=SETTINGS.api.secret_key)

# Register sub-routers
app.include_router(
    authentication_router, prefix="/authentication", tags=["authentication"]
)
app.include_router(
    canned_responses_router,
    prefix="/canned-responses",
    tags=["canned-responses"],
    dependencies=[Depends(is_logged_in)],
)
app.include_router(
    panel_router,
    prefix="/panels",
    tags=["panels"],
    dependencies=[Depends(is_logged_in)],
)
app.include_router(
    tickets_router,
    prefix="/tickets",
    tags=["tickets"],
    dependencies=[Depends(is_logged_in)],
)
app.include_router(static_router, tags=["static"])


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request: Request, exception: StarletteHTTPException):
    return UJSONResponse(
        {"success": False, "reason": exception.detail},
        status_code=exception.status_code,
        headers=getattr(exception, "headers", None),
    )


@app.on_event("startup")
async def on_startup():
    await DISCORD.login(SETTINGS.discord_token)


@app.on_event("shutdown")
async def on_shutdown():
    await DISCORD.logout()
