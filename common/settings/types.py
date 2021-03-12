from pydantic import AnyUrl, PostgresDsn
import re
from typing import Union

DISCORD_TOKEN_REGEX = re.compile(r"^\w{24}\.\w{6}\.\w{27}$")


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


class SqliteDsn(AnyUrl):
    allowed_schemes = {"sqlite", "sqlite3"}


DatabaseUrl = Union[PostgresDsn, SqliteDsn]
