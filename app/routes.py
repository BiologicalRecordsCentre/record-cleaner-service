import logging

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.settings import Config

import app.auth as auth
import app.main as app
# from app.county.county_routes import router as county_router
from app.rule.rule_routes import router as rule_router
from app.settings import settings
from app.species.species_routes import router as species_router
from app.user.user_routes import router as user_router
from app.validate.validate_routes import router as validate_router
from app.verify.verify_routes import router as verify_router

logger = logging.getLogger(__name__)


class Service(BaseModel):
    title: str
    version: str
    summary: str
    contact: str
    docs_url: str
    swagger_url: str
    code_repo: str
    rules_repo: str
    rules_branch: str
    rules_commit: str
    maintenance_mode: bool
    maintenance_message: str


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
# router.include_router(county_router)


@router.get(
    "/",
    tags=['Service'],
    summary="Show service information.",
    response_model=Service)
async def read_service(request: Request):
    logger.info('TEST TEST TEST TEST TEST TEST')
    base_url = str(request.base_url)[:-1]
    return Service(
        title=app.app.title,
        version=app.app.version,
        summary=app.app.summary,
        contact=app.app.contact['email'],
        docs_url="https://biologicalrecordscentre.github.io/record-cleaner-service/",
        swagger_url=base_url + app.app.docs_url,
        code_repo="https://github.com/BiologicalRecordsCentre/record-cleaner-service",
        rules_repo=settings.env.rules_repo,
        rules_branch=settings.env.rules_branch,
        rules_commit=settings.db.rules_commit,
        maintenance_mode=settings.db.maintenance_mode,
        maintenance_message=settings.db.maintenance_message,
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
    dependencies=[Depends(auth.get_current_admin_user)]
)
async def read_settings(settings: Config):
    return settings.db.list()


@router.patch(
    "/settings",
    summary="Alter settings.",
    tags=['Service'],
    response_model=dict,
    dependencies=[Depends(auth.get_current_admin_user)]
)
async def patch_settings(settings: Config, new_settings: dict):
    for name, value in new_settings.items():
        setattr(settings.db, name, value)

    return settings.db.list()
