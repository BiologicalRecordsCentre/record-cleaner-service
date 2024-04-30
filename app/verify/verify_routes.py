from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth import get_current_user
import app.species.cache as cache
from app.utilities.srefs import Sref
from app.utilities.srefs.sref_factory import SrefFactory
from app.utilities.vice_counties.vc_checker import VcChecker
from app.utilities.vague_dates import VagueDate


router = APIRouter(
    prefix="/verify",
    tags=["Verify"],
    dependencies=[Depends(get_current_user)]
)


class Verify(BaseModel):
    id: int = Field(ge=1)
    date: str
    sref: Sref


class VerifyName(Verify):
    name: str


class VerifyTvk(Verify):
    tvk: str = Field(min_length=1)


class Verified(Verify):
    name: Optional[str] = None
    tvk: Optional[str] = None
    ok: bool = True
    message: Optional[str] = None


@router.post(
    "/records_by_tvk",
    summary="Verify records identified by TVK.",
    response_model=list[Verified])
async def verify_by_tvk(records: list[VerifyTvk]):

    results = []
    for record in records:
        # Our response begins with the input data.
        result_data = record.model_dump()

        try:
            # 1. Get preferred TVK.
            taxon = cache.get_taxon_by_tvk(record.tvk)
            result_data['tvk'] = taxon.preferred_tvk
            result_data['name'] = taxon.preferred_name

            # 2. Format date.
            vague_date = VagueDate(record.date)
            result_data['date'] = str(vague_date)

            # 3. Obtain gridref.
            sref = SrefFactory(record.sref)
            result_data['sref'] = sref.model_dump()

            # 4. Check against rules.

            results.append(Verified(**result_data))

        except ValueError as e:
            result_data['ok'] = False
            result_data['message'] = str(e)
            results.append(Verified(**result_data))
            continue

    return results


@router.post(
    "/records_by_name",
    summary="Verify records identified by name.",
    response_model=list[Verified])
async def verify_by_name(records: list[VerifyName]):

    results = []
    return results
