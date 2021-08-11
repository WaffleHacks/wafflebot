from datetime import datetime
from dotenv import load_dotenv
from os import environ
from pydantic import BaseModel

from .api import ApiSettings
from .bot import BotSettings
from .types import DiscordToken, PostgresDsn, RedisDsn

API_PREFIX = "api_"
BOT_PREFIX = "bot_"


class Settings(BaseModel):
    api: ApiSettings
    bot: BotSettings

    full_errors: bool = False

    database_url: PostgresDsn
    discord_token: DiscordToken
    redis_url: RedisDsn

    event_start: datetime
    event_end: datetime


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

    return Settings(**raw_settings)
