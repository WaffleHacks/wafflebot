from aiofiles.os import stat as aio_stat
from email.utils import parsedate
from fastapi import Request, Response
import os.path
from starlette.datastructures import Headers
from starlette.staticfiles import FileResponse, NotModifiedResponse
from typing import Optional, Tuple

from common import SETTINGS


STATIC_PATH = "frontend/public"


async def lookup_path(path: str) -> Tuple[str, Optional[os.stat_result]]:
    """
    Get the full path to the requested file and check if it exists
    :param path: the relative path to the file
    :return: the absolute path to and stat of the file
    """
    # Get the paths
    normalized = os.path.normpath(os.path.join(*path.split("/")))
    full_path = os.path.realpath(os.path.join(STATIC_PATH, normalized))
    directory = os.path.realpath(STATIC_PATH)

    # Prevent escaping the static files dir
    if os.path.commonprefix([full_path, directory]) != directory:
        return "", None

    # Check if the file exists
    try:
        stat_result = await aio_stat(full_path)
        return full_path, stat_result
    except FileNotFoundError:
        return "", None


def is_not_modified(response_headers: Headers, request_headers: Headers) -> bool:
    """
    Check if a not modified response should be returned
    :param response_headers: the headers for the response
    :param request_headers: the headers for the request
    :return: whether the browser should use the cached data
    """
    try:
        # Check If-None-Match header
        if_none_match = request_headers["if-none-match"]
        etag = response_headers["etag"]
        if if_none_match == etag:
            return True

        # Check If-Modified-Since header
        if_modified_since = parsedate(request_headers["if-modified-since"])
        last_modified = parsedate(response_headers["last-modified"])
        if (
            if_modified_since is not None
            and last_modified is not None
            and if_modified_since >= last_modified
        ):
            return True
    except KeyError:
        pass

    return False


def file_response(path: str, stat_result: os.stat_result, request: Request) -> Response:
    """
    Generate the response for the file
    :param path: the full path to the file
    :param stat_result: the stat of the file
    :param request: the incoming request
    :return: a response for the request
    """
    # Generate the response
    response = FileResponse(path, stat_result=stat_result, method=request.method)

    # Check if not modified
    if is_not_modified(response.headers, request.headers):
        return NotModifiedResponse(response.headers)

    return response
