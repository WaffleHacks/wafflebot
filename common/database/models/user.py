from pydantic import validator
import re
from typing import Optional

from .base import Model, find_primary_key
from ..tables import users

DISCORD_AVATAR_REGEX = re.compile(
    r"^https://cdn\.discordapp\.com/avatars/\d{1,19}/[a-f0-9]+\.png$"
)
DISCORD_USERNAME_REGEX = re.compile(r"^[^#]{2,32}#\d{4}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class User(Model):
    __table__ = users
    __primary_key__ = find_primary_key(users)

    id: Optional[int]
    email: str
    username: str
    avatar: str
    has_panel: bool

    @validator("email")
    def email_follows_rfc2821(cls, v: str):
        if EMAIL_REGEX.fullmatch(v) is None:
            raise ValueError("email must follow the rfc2821 format")
        return v

    @validator("email")
    def email_is_proper_length(cls, v: str):
        if len(v) < 5 or len(v) > 254:
            raise ValueError("email must be between 5 and 254 characters in length")
        return v

    @validator("username")
    def username_matches_regex(cls, v: str):
        if DISCORD_USERNAME_REGEX.fullmatch(v) is None:
            raise ValueError("username has invalid format")
        return v

    @validator("avatar")
    def avatar_is_url(cls, v: str):
        if DISCORD_AVATAR_REGEX.fullmatch(v) is None:
            raise ValueError("avatar must be a Discord CDN url")
        return v
