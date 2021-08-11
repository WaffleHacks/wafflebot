from pydantic import BaseModel
from .types import DiscordClientSecret


class ApiSettings(BaseModel):
    secret_key: str

    discord_client_id: str
    discord_client_secret: DiscordClientSecret

    guild_id: int

    class Config:
        env_prefix = "API_"
