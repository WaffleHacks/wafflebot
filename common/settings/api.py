from pydantic import BaseModel


class ApiSettings(BaseModel):
    class Config:
        env_prefix = "API_"
