from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

import app.auth as auth
import app.species.cache as cache
from . import srefs as srefs
from .vice_counties.vc_checker import VcChecker
from .vague_dates import VagueDate


router = APIRouter()
vc_checker = VcChecker()


class Validate(BaseModel):
    id: int
    date: str
    sref: str
    sref_system: srefs.SrefSystem
    vc: Optional[str | int] = None


class ValidateName(Validate):
    name: str


class ValidateTvk(Validate):
    tvk: str


class Validateed(Validate):
    name: Optional[str] = None
    tvk: Optional[str] = None
    ok: bool = True
    message: Optional[str] = None


@router.post(
    "/validate/records_by_tvk",
    tags=['Validate'],
    summary="Validate records identified by TVK.",
    response_model=list[Validateed])
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
            result_data['name'] = taxon.name

            # 2. Confirm date is valid.
            vague_date = VagueDate(record.date)
            result_data['date'] = str(vague_date)

            # 3. Confirm sref is valid.
            # Look up the class for the sref system.
            sref_system_class = srefs.class_map[record.sref_system]
            # Instantiate an sref object of that class.
            sref = sref_system_class(record.sref)

            # 4. Check sref in vice county.
            if record.vc is not None:
                code = vc_checker.prepare_code(record.vc)
                result_data['vc'] = code
                gridref = vc_checker.prepare_gridref(sref.gridref)
                vc_checker.check(gridref, code)

            results.append(Validateed(**result_data))

        except ValueError as e:
            result_data['ok'] = False
            result_data['message'] = str(e)
            results.append(Validateed(**result_data))
            continue

    return results


@router.post(
    "/validate/records_by_name",
    tags=['Validate'],
    summary="Validate records identified by name.",
    response_model=list[Validateed])
async def validate_by_name(
        auth: auth.Auth,
        records: list[ValidateName]):

    results = []
    return results
