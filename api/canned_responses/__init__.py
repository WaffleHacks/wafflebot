from asyncpg.exceptions import UniqueViolationError
from fastapi import APIRouter, HTTPException
import json
from typing import List

from common.database import CannedResponse
from .models import CannedResponse as CannedResponseModel, UpdateCannedResponse

router = APIRouter()


@router.get("/", response_model=List[CannedResponseModel])
async def list_responses():
    responses = await CannedResponse.objects.all()

    # Parse the fields in the response
    for response in responses:
        response.fields = json.loads(response.fields)

    return responses


@router.post("/")
async def create(response: CannedResponse):
    # Remove the id field
    params = response.dict()
    params.pop("id", None)

    try:
        return await CannedResponse.objects.create(**params)
    except UniqueViolationError:
        raise HTTPException(status_code=409, detail="field 'key' must be unique")


@router.get("/{primary_key}", response_model=CannedResponseModel)
async def get(primary_key: int):
    response = await CannedResponse.objects.filter(id=primary_key).get()
    if response is None:
        raise HTTPException(status_code=404, detail="not found")

    # Parse the fields
    response.fields = json.loads(response.fields)

    return response


@router.put("/{primary_key}", response_model=CannedResponseModel)
async def update(primary_key: int, fields: UpdateCannedResponse):
    # Get the response
    response = await CannedResponse.objects.filter(id=primary_key).get()
    if response is None:
        raise HTTPException(status_code=404, detail="not found")

    # Get the updated fields, excluding unset ones
    params = fields.dict(exclude_none=True, exclude_unset=True)

    # Commit the changes
    try:
        await response.update(**params)
    except UniqueViolationError:
        raise HTTPException(status_code=409, detail="field 'key' must be unique")

    response.fields = json.loads(response.fields)
    return response


@router.delete("/{primary_key}")
async def delete(primary_key: int):
    # Get the response
    response = await CannedResponse.objects.get(id=primary_key)

    # Delete it if it exists
    if response is not None:
        await response.delete()

    return {"success": True}
