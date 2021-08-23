from pydantic import BaseModel
from typing import Literal


class UpdateDiscordQuestionnaire(BaseModel):
    discord: str


class UpdateDiscord(BaseModel):
    type: Literal["questionnaire_discord"]
    questionnaire: UpdateDiscordQuestionnaire
