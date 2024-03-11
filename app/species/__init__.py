from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Indicia is the current source of taxon data but one day, maybe, there will
# be a UKSI API. For this reason, it is abstracted into its own module.
import app.species.indicia as driver
import app.auth as auth

router = APIRouter()
router.include_router(driver.router)


class Taxon(BaseModel):
    external_key: str
    organism_key: str
    taxon: str
    preferred_taxon: str


@router.get("/taxon_by_tvk", response_model=Taxon)
async def read_taxon(
        auth: auth.Auth,
        tvk: str):

    if tvk:
        taxon = driver.get_taxon_by_tvk(tvk)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide either tvk or name")

    return Taxon(**taxon)


@router.get("/taxon_by_name, response_model=Taxon")
async def read_taxon_by_name(
        auth: auth.Auth,
        name: str):

    if name:
        taxon = driver.get_taxon_by_name(name)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide either tvk or name")

    return Taxon(**taxon)
