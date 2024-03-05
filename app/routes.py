from datetime import datetime
import re
from typing import Annotated

from fastapi import APIRouter, Depends

import app.auth as auth
import app.species as species

# Instantiate a router.
router = APIRouter()
router.include_router(auth.router)
router.include_router(species.router)


@router.get("/")
async def read_root():
    return {"Hello": "FastAPI!"}


@router.get("/hello/{name}")
@router.get("/hello")
async def read_name(
        auth: Annotated[bool, Depends(auth.authenticate)],
        name=None):
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %X")

    match_object = None
    if name:
        match_object = re.match("[a-zA-Z]+", name)

    if match_object:
        clean_name = match_object.group(0)
    else:
        clean_name = "Friend"

    content = "Hello there, " + clean_name + "! It's " + formatted_now
    return {"content": content}
