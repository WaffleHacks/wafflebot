from pydantic import BaseModel
from .types import DiscordClientSecret


class ApiSettings(BaseModel):
    secret_key: str

    discord_client_id: str
    discord_client_secret: DiscordClientSecret

    webhook_secret: str

    class Config:
        env_prefix = "API_"
