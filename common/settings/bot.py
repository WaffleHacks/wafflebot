from pydantic import BaseModel


class BotSettings(BaseModel):
    log_file: str = "discord.log"

    class Config:
        env_prefix = "BOT_"
