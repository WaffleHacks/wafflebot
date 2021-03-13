from pydantic import BaseModel


class BotSettings(BaseModel):
    log_file: str = "discord.log"
    registration_config: str = "registration.json"

    class Config:
        env_prefix = "BOT_"
