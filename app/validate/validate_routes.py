from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth import get_current_user
from app.database import DB
import app.species.cache as cache
from app.utilities.srefs import Sref
from app.utilities.srefs.sref_factory import SrefFactory
from app.utilities.vice_counties.vc_checker import VcChecker
from app.utilities.vague_dates import VagueDate


router = APIRouter(
    prefix="/validate",
    tags=["Validate"],
    dependencies=[Depends(get_current_user)]
)


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
    "/records_by_tvk",
    summary="Validate records identified by TVK.",
    response_model=list[Validated])
async def validate_by_tvk(session: DB, records: list[ValidateTvk]):

    results = []
    for record in records:
        # Our response begins with the input data.
        result_data = record.model_dump()

        try:
            # 1. Confirm TVK is valid.
            taxon = cache.get_taxon_by_tvk(session, record.tvk)
            if taxon is None:
                raise ValueError("TVK not recognised.")
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
                code = VcChecker.prepare_code(record.vc)
                # Return code if name was supplied.
                result_data['vc'] = code
                gridref = VcChecker.prepare_sref(sref.gridref)
                VcChecker.check(gridref, code)

            results.append(Validated(**result_data))

        except ValueError as e:
            result_data['ok'] = False
            result_data['message'] = str(e)
            results.append(Validated(**result_data))
            continue

    return results


@router.post(
    "/records_by_name",
    summary="Validate records identified by name.",
    response_model=list[Validated])
async def validate_by_name(session: DB, records: list[ValidateName]):

    results = []
    return results
