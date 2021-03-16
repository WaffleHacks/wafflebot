from fastapi import APIRouter, Request
import os.path
from starlette.responses import PlainTextResponse, RedirectResponse, URL
import stat

from . import utils

router = APIRouter()


@router.get("/")
@router.get("/{path:path}")
async def index(request: Request, path: str):
    # Check if the full path to the file exists
    full_path, stat_result = await utils.lookup_path(path)

    # If the path exists and is a file, return it
    if stat_result and stat.S_ISREG(stat_result.st_mode):
        return utils.file_response(full_path, stat_result, request)

    # If the path exists and is a directory, return the index.html under it
    elif stat_result and stat.S_ISDIR(stat_result.st_mode):
        # Build the new path to the index
        index_path = os.path.join(path, "index.html")
        full_path, stat_result = await utils.lookup_path(index_path)

        # Check if the file exists
        if stat_result is not None and stat.S_ISREG(stat_result.st_mode):
            # Redirect to directory with slash
            if not path.endswith("/") and path != "":
                url = URL(scope=request.scope)
                url = url.replace(path=url.path + "/")
                return RedirectResponse(url)

            return utils.file_response(full_path, stat_result, request)

    # Return the index if not found
    else:
        # Build the new path
        full_path, stat_result = await utils.lookup_path("index.html")

        # Check if file exists
        if stat_result is not None and stat.S_ISREG(stat_result.st_mode):
            return utils.file_response(full_path, stat_result, request)

    return PlainTextResponse("Not Found", status_code=404)
