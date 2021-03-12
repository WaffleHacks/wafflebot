from pydantic import BaseSettings

from .types import DatabaseUrl


class Settings(BaseSettings):
    database_url: DatabaseUrl

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
