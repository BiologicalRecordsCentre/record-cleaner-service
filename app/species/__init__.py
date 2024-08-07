from fastapi import APIRouter, HTTPException, status

import app.auth as auth
from app.database import DB
import app.species.cache as cache
# Indicia is the current source of taxon data but one day, maybe, there will
# be a UKSI API. For this reason, it is abstracted into its own module.
import app.species.indicia as driver
from app.sqlmodels import Taxon

router = APIRouter()
router.include_router(driver.router)
router.include_router(cache.router)


@router.get(
    "/species/taxon_by_tvk/{tvk}",
    tags=['Species'],
    summary="Get taxon with given TVK.",
    response_model=Taxon)
async def read_taxon_by_tvk(
        auth: auth.Auth,
        session: DB,
        tvk: str):

    try:
        taxon = cache.get_taxon_by_tvk(session, tvk)
        if taxon is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Taxon not found with TVK {tvk}.")

        return taxon

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))


@router.get(
    '/species/taxon_by_name/{name}',
    tags=['Species'],
    summary="Get taxon with given name.",
    response_model=Taxon)
async def read_taxon_by_name(
        auth: auth.Auth,
        session: DB,
        name: str):

    try:
        taxon = cache.get_taxon_by_name(session, name)
        if taxon is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Taxon not found with name {name}.")

        return taxon

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))
