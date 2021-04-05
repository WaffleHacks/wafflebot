from fastapi import APIRouter, Depends, HTTPException
from typing import List

from common import CONFIG, ConfigKey
from .models import SettingUpdate, SettingResponse

router = APIRouter()


@router.get("/", response_model=List[SettingResponse])
async def get():
    response = []

    # Iterate over all the config keys and get their values
    for key in ConfigKey:
        # Get the value
        result = await getattr(CONFIG, key.value)()

        # Add it to the response
        response.append(SettingResponse(key=key.value, value=result))

    return response


@router.put("/{key}", response_model=SettingResponse)
async def update(key: ConfigKey, fields: SettingUpdate):
    # Check if array field
    if key in ConfigKey.exclude_autogenerated():
        # Ensure action is provided
        if fields.action is None:
            raise HTTPException(
                status_code=400, detail="action is required for array fields"
            )

        # Add or remove the value
        await getattr(CONFIG, f"{fields.action.value}_{key.value}")(fields.value)

        # Get the resulting value
        new = await getattr(CONFIG, key.value)()
        return SettingResponse(key=key, value=new)

    # Ensure the value to set isnt an array
    if isinstance(fields.value, list):
        raise HTTPException(
            status_code=400, detail="list only accepted for array config keys"
        )

    # Set the new value
    await getattr(CONFIG, key.value)(fields.value)

    return SettingResponse(key=key, value=fields.value)
