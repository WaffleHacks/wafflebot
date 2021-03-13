from pydantic import BaseModel


class UserInfo(BaseModel):
    """
    A user's profile information
    """

    id: str
    username: str
    email: str
    email_verified: bool
    picture: str
