
from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.database import DB
from app.rule.difficulty.difficulty_rule_repo import DifficultyRuleRepo
import app.species.cache as cache
from app.utility.sref.sref_factory import SrefFactory
from app.utility.vice_county.vc_checker import VcChecker
from app.utility.vague_date import VagueDate

from .validate_models import ValidateTvk, ValidateName, Validated

router = APIRouter(
    prefix="/validate",
    tags=["Validate"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/records_by_tvk",
    summary="Validate records identified by TVK.",
    response_model=list[Validated])
async def validate_by_tvk(session: DB, records: list[ValidateTvk]):

    results = []
    for record in records:
        # Our response begins with the input data.
        result = Validated(**record.model_dump())

        try:
            # 1. Confirm TVK is valid.
            taxon = cache.get_taxon_by_tvk(session, record.tvk)
            if taxon is None:
                raise ValueError("TVK not recognised.")
            # Return name associated with TVK.
            result.name = taxon.name

            # 2. Confirm date is valid.
            vague_date = VagueDate(record.date)
            # Return date in preferred format.
            result.date = str(vague_date)

            # 3. Confirm sref is valid.
            sref = SrefFactory(record.sref)
            if record.sref.gridref is not None:
                # Return cleaned up gridref.
                result.sref.gridref = sref.gridref

            # 4. Check sref in vice county.
            if record.vc is not None:
                code = VcChecker.prepare_code(record.vc)
                # Return code if name was supplied.
                result.vc = code
                gridref = VcChecker.prepare_sref(sref.gridref)
                VcChecker.check(gridref, code)

            # 5. Get id difficulty.
            repo = DifficultyRuleRepo(session)
            result.id_difficulty = repo.run(record)

            results.append(result)

        except ValueError as e:
            result.ok = False
            result.message = str(e)
            results.append(result)
            continue

    return results


@router.post(
    "/records_by_name",
    summary="Validate records identified by name.",
    response_model=list[Validated])
async def validate_by_name(session: DB, records: list[ValidateName]):

    results = []
    return results
