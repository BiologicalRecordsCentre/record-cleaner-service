from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

import app.auth as auth
import app.species.cache as cache
from app.utilities.srefs import Sref
from app.utilities.srefs.sref_factory import SrefFactory
from app.utilities.vice_counties.vc_checker import VcChecker
from app.utilities.vague_dates import VagueDate


router = APIRouter()


class Validate(BaseModel):
    id: int = Field(ge=1)
    date: str
    sref: Sref
    vc: Optional[str | int] = None


class ValidateName(Validate):
    name: str


class ValidateTvk(Validate):
    tvk: str = Field(min_length=1)


class Validated(Validate):
    name: Optional[str] = None
    tvk: Optional[str] = None
    ok: bool = True
    message: Optional[str] = None


@router.post(
    "/verify/records_by_tvk",
    tags=['Verify'],
    summary="Verify records identified by TVK.",
    response_model=list[Validated])
async def verify_by_tvk(
        auth: auth.Auth,
        records: list[ValidateTvk]):

    results = []
    for record in records:
        # Our response begins with the input data.
        result_data = record.model_dump()

        try:
            # 1. Get preferred TVK.
            taxon = cache.get_taxon_by_tvk(record.tvk)

            # 2. Format date.
            vague_date = VagueDate(record.date)

            # 3. Obtain gridref.
            sref = SrefFactory(record.sref)
            gridref = sref.gridref

            results.append(Validated(**result_data))

        except ValueError as e:
            result_data['ok'] = False
            result_data['message'] = str(e)
            results.append(Validated(**result_data))
            continue

    return results


@router.post(
    "/verify/records_by_name",
    tags=['Verify'],
    summary="Verify records identified by name.",
    response_model=list[Validated])
async def verify_by_name(
        auth: auth.Auth,
        records: list[ValidateName]):

    results = []
    return results
