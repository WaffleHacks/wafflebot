from datetime import datetime
from dotenv import load_dotenv
from enum import Enum
from os import environ
from pydantic import BaseModel, root_validator
from typing import Optional

from .api import ApiSettings
from .bot import BotSettings
from .types import DiscordToken, PostgresDsn, RedisDsn

API_PREFIX = "api_"
BOT_PREFIX = "bot_"


class Mode(Enum):
    API = "api"
    BOT = "bot"
    BOTH = "both"


class Settings(BaseModel):
    api: Optional[ApiSettings]
    bot: Optional[BotSettings]

    mode: Mode = Mode.BOTH

    full_errors: bool = False

    database_url: PostgresDsn
    redis_url: RedisDsn

    discord_token: DiscordToken
    discord_guild_id: int

    sentry_dsn: Optional[str]

    event_start: datetime
    event_end: datetime

    @root_validator
    def section_required(cls, values):
        mode = values["mode"]
        if mode == Mode.BOTH and (
            values.get("api") is None or values.get("bot") is None
        ):
            raise ValueError("settings for api and bot are required")
        elif mode == Mode.API and values.get("api") is None:
            raise ValueError("settings for api are required")
        elif mode == Mode.BOT and values.get("bot") is None:
            raise ValueError("settings for bot are required")

        return values


def load_settings() -> Settings:
    # Load settings from the environment
    load_dotenv()

    raw_settings = {"api": {}, "bot": {}}
    for key, value in environ.items():
        key = key.lower()
        if key == "api" or key == "bot":
            raise ValueError(f"configuration key '{key}' cannot be 'API' or 'BOT'")

        if key.startswith(API_PREFIX):
            raw_settings["api"][key[4:]] = value
        elif key.startswith(BOT_PREFIX):
            raw_settings["bot"][key[4:]] = value
        else:
            raw_settings[key] = value

    if raw_settings["api"] == {}:
        raw_settings["api"] = None
    if raw_settings["bot"] == {}:
        raw_settings["bot"] = None

    return Settings(**raw_settings)
