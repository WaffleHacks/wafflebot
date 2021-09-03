from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.responses import UJSONResponse
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from common import CONFIG, SETTINGS
from .announcements import router as announcements_router
from .authentication import router as authentication_router
from .canned_responses import router as canned_responses_router
from .settings import router as settings_router
from .static import router as static_router
from .webhooks import router as webhooks_router
from .utils.client import DISCORD
from .utils.session import is_logged_in

app = FastAPI(docs_url=None, swagger_ui_oauth2_redirect_url=None, redoc_url="/docs")

# Integrate with Sentry
sentry_sdk.init(
    dsn=SETTINGS.sentry_dsn,
    integrations=[SqlalchemyIntegration()],
    traces_sample_rate=1.0,
    environment="development" if SETTINGS.full_errors else "production",
    send_default_pii=True,
)

# Register middleware
app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(SessionMiddleware, secret_key=SETTINGS.api.secret_key)

# Register API routers
api = APIRouter(prefix="/api")
api.include_router(
    announcements_router,
    prefix="/announcements",
    tags=["announcements"],
    dependencies=[Depends(is_logged_in)],
)
api.include_router(
    authentication_router, prefix="/authentication", tags=["authentication"]
)
api.include_router(
    canned_responses_router,
    prefix="/canned-responses",
    tags=["canned-responses"],
    dependencies=[Depends(is_logged_in)],
)
api.include_router(
    settings_router,
    prefix="/settings",
    tags=["settings"],
    dependencies=[Depends(is_logged_in)],
)
api.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])

# Include routers
app.include_router(api)
app.include_router(static_router, tags=["static"])


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request: Request, exception: StarletteHTTPException):
    return UJSONResponse(
        {"success": False, "reason": exception.detail},
        status_code=exception.status_code,
        headers=getattr(exception, "headers", None),
    )


@app.exception_handler(500)
async def unknown_exception_handler(_request: Request, exception: Exception):
    sentry_sdk.capture_exception(exception)
    return UJSONResponse(
        {"success": False, "reason": "internal server error"}, status_code=500
    )


@app.on_event("startup")
async def on_startup():
    await CONFIG.connect()
    await DISCORD.login(SETTINGS.discord_token)


@app.on_event("shutdown")
async def on_shutdown():
    await CONFIG.disconnect()
    await DISCORD.close()
