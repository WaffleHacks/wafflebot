from fastapi import FastAPI, Request
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from common import SETTINGS
from common.database import database
from .authentication import router as authentication_router

app = FastAPI()

# Register middleware
app.add_middleware(SessionMiddleware, secret_key=SETTINGS.api.secret_key)

# Mount apps and sub-apps
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(
    authentication_router, prefix="/authentication", tags=["authentication"]
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request: Request, exception: StarletteHTTPException):
    return UJSONResponse(
        {"success": False, "reason": exception.detail},
        status_code=exception.status_code,
        headers=getattr(exception, "headers", None),
    )
