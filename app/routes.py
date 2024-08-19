from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.settings import Config

import app.auth as auth
import app.main as app
from app.rule.rule_routes import router as rule_router
from app.settings import settings
from app.species.species_routes import router as species_router
from app.user.user_routes import router as user_router
from app.validate.validate_routes import router as validate_router
from app.verify.verify_routes import router as verify_router


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


class SettingResponse(BaseModel):
    name: str
    value: str | int | bool


# Instantiate a router.
router = APIRouter()
router.include_router(auth.router)
router.include_router(rule_router)
router.include_router(species_router)
router.include_router(user_router)
router.include_router(validate_router)
router.include_router(verify_router)


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
    response_model=Maintenance,
    dependencies=[Depends(auth.get_current_admin_user)]
)
async def set_maintenance(maintenance: Maintenance):
    settings.db.maintenance_mode = maintenance.mode
    settings.db.maintenance_message = maintenance.message
    return maintenance


@router.get(
    "/settings",
    tags=['Service'],
    summary="List settings.",
    response_model=dict,
    #    dependencies=[Depends(auth.get_current_admin_user)]
)
async def read_settings(settings: Config):
    return settings.db.list()


@router.patch(
    "/settings",
    summary="Alter settings.",
    tags=['Service'],
    response_model=dict,
    #    dependencies=[Depends(auth.get_current_admin_user)]
)
async def patch_settings(settings: Config, new_settings: dict):
    for name, value in new_settings.items():
        setattr(settings.db, name, value)

    return settings.db.list()
