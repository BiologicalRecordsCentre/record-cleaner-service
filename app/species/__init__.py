from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

import app.species.indicia as driver

router = APIRouter()


class Taxon(BaseModel):
    tvk: str
    org: str
    name: str


@router.get("/species/{name}, response_model=Taxon")
async def read_species_by_name(
        taxon: Annotated[Taxon, Depends(driver.get_taxon_by_name)]
):
    return taxon


@router.get("/species/{tvk}, response_model=Taxon")
async def read_species_by_tyk(
        taxon: Annotated[Taxon, Depends(driver.get_taxon_by_tvk)]
):
    return taxon
