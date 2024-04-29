from fastapi import APIRouter
from pydantic import BaseModel

from app.auth import Auth
from app.database import DB

import app.auth as auth
import app.main as app
import app.rules as rules
from app.settings import settings
import app.species as species
import app.validate as validate
import app.users as users


class Service(BaseModel):
    title: str
    version: str
    summary: str
    docs_url: str
    maintenance_mode: bool
    maintenance_message: str
    rules_commit: str


class Maintenance(BaseModel):
    mode: bool
    message: str


# Instantiate a router.
router = APIRouter()
router.include_router(auth.router)
router.include_router(rules.router)
router.include_router(species.router)
router.include_router(validate.router)
router.include_router(users.router)  # prefix="/users", tags=["Users"]


@router.get(
    "/",
    tags=['Service'],
    summary="Show service information.",
    response_model=Service)
async def read_service():
    return Service(
        title=app.app.title,
        version=app.app.version,
        summary=app.app.summary,
        docs_url=app.app.docs_url,
        maintenance_mode=settings.db.maintenance_mode,
        maintenance_message=settings.db.maintenance_message,
        rules_commit=settings.db.rules_commit
    )


@router.post(
    "/maintenance",
    summary="Set maintenance information.",
    tags=['Service'],
    response_model=Maintenance
)
async def set_maintenance(
    token: Auth,
    maintenance: Maintenance
):
    settings.db.maintenance_mode = maintenance.mode
    settings.db.maintenance_message = maintenance.message
    return maintenance


@router.get(
    "/settings",
    tags=['Service'],
    summary="List settings.",
    response_model=Service)
async def read_service(token: auth.Auth):
    return Service(
        title=app.app.title,
        version=app.app.version,
        summary=app.app.summary,
        docs_url=app.app.docs_url,
        maintenance_mode=settings.db.maintenance_mode,
        maintenance_message=settings.db.maintenance_message,
        rules_commit=settings.db.rules_commit
    )


@router.post(
    "/maintenance",
    summary="Set maintenance information.",
    tags=['Service'],
    response_model=Maintenance
)
async def set_maintenance(
    token: auth.Auth,
    maintenance: Maintenance
):
    settings.db.maintenance_mode = maintenance.mode
    settings.db.maintenance_message = maintenance.message
    return maintenance
