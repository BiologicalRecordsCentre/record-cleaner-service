import logging

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.auth import AdminDependency, get_current_admin_user
import app.main as app
# from app.county.county_routes import router as county_router
from app.auth import router as auth_router
from app.county.county_routes import router as county_router
from app.rule.rule_routes import router as rule_router
from app.settings import SettingsDependency
from app.species.species_routes import router as species_router
from app.user.user_routes import router as user_router
from app.validate.validate_routes import router as validate_router
from app.verify.verify_routes import router as verify_router

logger = logging.getLogger(f"uvicorn.{__name__}")


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
router.include_router(auth_router)
router.include_router(rule_router)
router.include_router(species_router)
router.include_router(user_router)
router.include_router(validate_router)
router.include_router(verify_router)
router.include_router(county_router)


@router.get(
    "/",
    tags=['Service'],
    summary="Show service information.",
    response_model=Service)
async def read_service(request: Request, settings: SettingsDependency):
    """Returns information about the service.
    - **code_repo** and **version** tell what code is running.
    - **rules_repo**, **rules_branch** and **rules_commit** tell what rules are
      in use.
    - **maintenance_mode** is true if the service is under maintenance. In this
      mode, access to the service is limited.
    - **maintenance_message** may explain the cause and extent of maintenance.
    - **swagger_url** is the URL of the interactive API documentation.
    - **docs_url** is the URL of the static documentation.
    """
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
    response_model=Maintenance
)
async def set_maintenance(
    maintenance: Maintenance,
    user: AdminDependency,
    settings: SettingsDependency
):
    """Used by administrators to enable and disable maintenance mode."""
    settings.db.maintenance_mode = maintenance.mode
    settings.db.maintenance_message = maintenance.message
    logger.warning(
        "Maintenance mode set to %s by %s.",
        maintenance.mode,
        user.name)
    return maintenance


@router.get(
    "/settings",
    tags=['Service'],
    summary="List settings.",
    response_model=dict,
    dependencies=[Depends(get_current_admin_user)]
)
async def read_settings(settings: SettingsDependency):
    """The current settings include
    - **maintenance_mode**, true if the service is under maintenance.
    - **maintenance_message** explains the cause and extent of maintenance.
    - **rules_commit** is the commit hash of the rules currently in use.
    - **rules_updating** is true if a rule update is in progress. Since 
      updating the rules can lock the database, it is likely that the service
      will be in maintenance mode while a rule update happens.
    - **rules_updating_now** is an indication of progress during rule updates.
    - **rules_update_result** is a list of messages arising from the last rule
      update. This can indicate errors in rule files, for example."""
    return settings.db.list()


@router.patch(
    "/settings",
    summary="Alter settings.",
    tags=['Service'],
    response_model=dict,
    dependencies=[Depends(get_current_admin_user)]
)
async def patch_settings(settings: SettingsDependency, new_settings: dict):
    """Submit a dictionary of settings to change. E.g.
    **{"rules_updating": false}** may be useful if a problem occurs during rule
    updates."""
    for name, value in new_settings.items():
        setattr(settings.db, name, value)

    return settings.db.list()
