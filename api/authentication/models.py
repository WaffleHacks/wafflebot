from pydantic import BaseModel


class UserInfo(BaseModel):
    """
    A user's profile information
    """

    id: str
    username: str
    picture: str
    expiration: int
    is_admin: bool
