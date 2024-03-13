from fastapi import APIRouter
from pydantic import BaseModel

import app.auth as auth
import app.main as main
import app.species as species
import app.users as users


class Service(BaseModel):
    title: str
    version: str
    summary: str
    docs_url: str


# Instantiate a router.
router = APIRouter()
router.include_router(auth.router)
router.include_router(species.router)
router.include_router(users.router)


@router.get(
    "/",
    tags=['Service'],
    summary="Show service information.",
    response_model=Service)
async def read_service():
    return Service(
        title=main.app.title,
        version=main.app.version,
        summary=main.app.summary,
        docs_url=main.app.docs_url)
