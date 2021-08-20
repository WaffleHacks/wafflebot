from pydantic import BaseModel, validator
from typing import List, Optional


class BotSettings(BaseModel):
    log_file: Optional[str]

    disabled_extensions: List[str] = []

    hm_url: str = "https://apply.wafflehacks.tech"
    hm_client_id: str
    hm_client_secret: str

    teamup_api_key: str
    teamup_calendar: str

    class Config:
        env_prefix = "BOT_"

    @validator("disabled_extensions", pre=True)
    def format_modules(cls, value):
        if type(value) != str:
            raise TypeError("must be a string")

        if len(value.strip()) == 0:
            return []

        # Split the string on commas, remove any surrounding whitespace, and convert to lowercase
        return list(map(str.lower, map(str.strip, value.split(","))))
