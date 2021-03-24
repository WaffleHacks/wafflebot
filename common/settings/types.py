from pydantic import AnyUrl
import re
from typing import Union

DISCORD_TOKEN_REGEX = re.compile(r"^\w{24}\.\w{6}\.\w{27}$")
DISCORD_CLIENT_SECRET_REGEX = re.compile(r"^[a-zA-Z0-9-]{32}$")


class DiscordToken(str):
    @classmethod
    def __get_validators(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(pattern=DISCORD_TOKEN_REGEX.pattern)

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")
        elif not DISCORD_TOKEN_REGEX.fullmatch(v):
            raise ValueError("invalid discord bot token format")
        return v

    def __repr__(self):
        return f"DiscordToken({super().__repr__()[:24]}.{'*'*6}.{'*'*27})"


class DiscordClientSecret(str):
    @classmethod
    def __get_validators(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(patter=DISCORD_CLIENT_SECRET_REGEX.pattern)

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")
        elif not DISCORD_CLIENT_SECRET_REGEX.fullmatch(v):
            raise ValueError("invalid discord client secret format")
        return v


class PostgresDsn(AnyUrl):
    allowed_schemes = {"postgresql+asyncpg"}


DatabaseUrl = Union[PostgresDsn]
