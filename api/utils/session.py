from fastapi import Depends, HTTPException, Request
import time
from typing import Dict, List


async def get_session(request: Request) -> Dict:
    """
    Fetch the session data
    :param request: the incoming request
    """
    return request.session


async def is_logged_in(session=Depends(get_session)) -> Dict:
    """
    Ensure that the user is authenticated
    :param session: the session data
    """
    # Check that the user is logged in
    if not session.get("logged_in"):
        raise HTTPException(status_code=401, detail="unauthorized")

    # Check that the OAuth token hasn't expired
    expiration = session.get("token").get("expires_at")
    if time.time() > expiration:
        raise HTTPException(status_code=401, detail="unauthorized")

    return session


class Session(object):
    def __init__(self, key: str, required: bool = True):
        """
        Get the specified key out of the session
        :param key: the key to retrieve separated by `.`
        :param required: whether the parameter is required
        """
        self.key = key
        self.key_parts = key.split(".")
        self.required = required

    @staticmethod
    def __traverse(hierarchy: List[str], current):
        """
        Traverse down the key hierarchy to potentially get a value
        :param hierarchy: the levels of the key
        :param current: the current session data
        :return: the potential value
        """
        level = hierarchy.pop(0)
        if level not in current:
            return None
        elif len(hierarchy) == 0:
            return current.get(level)
        elif type(current[level]) != dict:
            return None
        else:
            return Session.__traverse(hierarchy, current[level])

    def __call__(self, session=Depends(get_session)):
        value = Session.__traverse(self.key_parts[:], session)

        # Raise an error if required
        if self.required and value is None:
            raise HTTPException(
                status_code=400, detail=f"missing cookie parameter '{self.key}'"
            )

        return value
