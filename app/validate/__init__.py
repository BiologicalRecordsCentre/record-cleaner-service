from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

import app.auth as auth
import app.species.cache as cache
from app.utilities.srefs import Sref
from app.utilities.srefs.sref_factory import SrefFactory
from app.utilities.vice_counties.vc_checker import VcChecker
from app.utilities.vague_dates import VagueDate


router = APIRouter()
vc_checker = VcChecker()


class Validate(BaseModel):
    id: int
    date: str
    sref: Sref
    vc: Optional[str | int] = None


class ValidateName(Validate):
    name: str


class ValidateTvk(Validate):
    tvk: str


class Validated(Validate):
    name: Optional[str] = None
    tvk: Optional[str] = None
    ok: bool = True
    message: Optional[str] = None


@router.post(
    "/validate/records_by_tvk",
    tags=['Validate'],
    summary="Validate records identified by TVK.",
    response_model=list[Validated])
async def validate_by_tvk(
        auth: auth.Auth,
        records: list[ValidateTvk]):

    results = []
    for record in records:
        # Our response begins with the input data.
        result_data = record.model_dump()

        try:
            # 1. Confirm TVK is valid.
            taxon = cache.get_taxon_by_tvk(record.tvk)
            # Return name associated with TVK.
            result_data['name'] = taxon.name

            # 2. Confirm date is valid.
            vague_date = VagueDate(record.date)
            # Return date in preferred format.
            result_data['date'] = str(vague_date)

            # 3. Confirm sref is valid.
            sref = SrefFactory(record.sref)
            if record.sref.gridref is not None:
                # Return cleaned up gridref.
                result_data['sref']['gridref'] = sref.gridref

            # 4. Check sref in vice county.
            if record.vc is not None:
                code = vc_checker.prepare_code(record.vc)
                # Return code if name was supplied.
                result_data['vc'] = code
                gridref = vc_checker.prepare_sref(sref.gridref)
                vc_checker.check(gridref, code)

            results.append(Validated(**result_data))

        except ValueError as e:
            result_data['ok'] = False
            result_data['message'] = str(e)
            results.append(Validated(**result_data))
            continue

    return results


@router.post(
    "/validate/records_by_name",
    tags=['Validate'],
    summary="Validate records identified by name.",
    response_model=list[Validated])
async def validate_by_name(
        auth: auth.Auth,
        records: list[ValidateName]):

    results = []
    return results
