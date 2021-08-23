from pydantic import BaseModel
from typing import Literal


class Questionnaire(BaseModel):
    discord: str


class Webhook(BaseModel):
    type: Literal["questionnaire_discord", "questionnaire_pending"]
    questionnaire: Questionnaire
