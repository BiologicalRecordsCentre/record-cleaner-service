from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

import app.auth as auth
import app.species.cache as cache
from . import srefs as srefs
from .vague_dates import VagueDate


router = APIRouter()


class Check(BaseModel):
    id: int
    date: str
    sref: str
    sref_system: srefs.SrefSystem
    vc: str | int


class CheckName(Check):
    name: str


class CheckTvk(Check):
    tvk: str


class Checked(Check):
    name: Optional[str] = None
    tvk: Optional[str] = None
    ok: bool = True
    message: Optional[str] = None


@router.post(
    "/check/records_by_tvk",
    tags=['Checks'],
    summary="Check records identified by TVK.",
    response_model=list[Checked])
async def check_by_tvk(
        auth: auth.Auth,
        records: list[CheckTvk]):

    results = []
    for record in records:
        # Our response begins with the input data.
        result_data = record.model_dump()

        try:
            # 1. Confirm TVK is valid.
            taxon = cache.get_taxon_by_tvk(record.tvk)

            if not taxon:
                result_data['ok'] = False
                result_data['message'] = 'Unknown TVK.'
                results.append(Checked(**result_data))
                continue
            else:
                result_data['name'] = taxon.name

            # 2. Confirm sref is valid.
            # Look up the class for the sref system.
            sref_system_class = srefs.class_map[record.sref_system]
            # Instantiate an sref object of that class.
            sref = sref_system_class(record.sref)
            if not sref.validate():
                result_data['ok'] = False
                result_data['message'] = 'Invalid spatial reference.'
                results.append(Checked(**result_data))
                continue

            # 3. Confirm date is valid.
            vague_date = VagueDate(record.date)
            result_data['date'] = str(vague_date)

            # 4. Check the record against the rules.
            results.append(Checked(**result_data))

        except ValueError as e:
            result_data['ok'] = False
            result_data['message'] = str(e)
            results.append(Checked(**result_data))
            continue

    return results


@router.post(
    "/check/records_by_name",
    tags=['Checks'],
    summary="Check records identified by name.",
    response_model=list[Checked])
async def check_by_name(
        auth: auth.Auth,
        records: list[CheckName]):

    results = []
    return results
