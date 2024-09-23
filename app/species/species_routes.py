from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.database import DbDependency
from app.settings_env import EnvDependency
import app.species.cache as cache
# Indicia is the current source of taxon data but one day, maybe, there will
# be a UKSI API. For this reason, it is abstracted into its own module.
import app.species.indicia as driver
from app.sqlmodels import Taxon

router = APIRouter(
    prefix="/species",
    dependencies=[Depends(get_current_user)]
)
router.include_router(driver.router)
router.include_router(cache.router)


@router.get(
    "/taxon_by_tvk/{tvk}",
    tags=["Species"],
    summary="Get taxon with given TVK.",
    response_model=Taxon)
async def read_taxon_by_tvk(
        db: DbDependency,
        env: EnvDependency,
        tvk: str):

    try:
        return cache.get_taxon_by_tvk(db, env, tvk)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))


@router.get(
    '/taxon_by_name/{name}',
    tags=["Species"],
    summary="Get taxon with given name.",
    response_model=Taxon)
async def read_taxon_by_name(
        db: DbDependency,
        env: EnvDependency,
        name: str):

    try:
        taxon = cache.get_taxon_by_name(db, env, name)
        if taxon is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Taxon not found with name {name}.")

        return taxon

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))
