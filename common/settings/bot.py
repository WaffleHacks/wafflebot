from pydantic import BaseModel


class BotSettings(BaseModel):
    log_file: str = "discord.log"

    hm_url: str = "https://apply.wafflehacks.tech"
    hm_client_id: str
    hm_client_secret: str

    class Config:
        env_prefix = "BOT_"
