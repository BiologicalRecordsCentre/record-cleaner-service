
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

        # 1. Confirm TVK is valid.
        try:
            taxon = cache.get_taxon_by_tvk(session, record.tvk)
            # Return preferred TVK.
            if record.tvk != taxon.preferred_tvk:
                result.tvk = taxon.preferred_tvk
                result.messages.append(
                    f"TVK '{record.tvk}' replaced by preferred TVK."
                )
            # Return preferred name.
            result.name = taxon.preferred_name

            # Get id difficulty.
            repo = DifficultyRuleRepo(session)
            result.id_difficulty = repo.run(record)

        except Exception as e:
            result.ok = False
            result.messages.append(str(e))

        # 2. Confirm date is valid.
        try:
            vague_date = VagueDate(record.date)
            # Return date in preferred format.
            result.date = str(vague_date)
        except Exception as e:
            result.ok = False
            result.messages.append(str(e))

        # 3. Confirm sref is valid.
        try:
            sref = SrefFactory(record.sref)
            if record.sref.gridref is not None:
                # Return cleaned up gridref.
                result.sref.gridref = sref.gridref

            # Check sref in vice county.
            if record.vc is not None:
                code = VcChecker.prepare_code(record.vc)
                # Return code if name was supplied.
                result.vc = code
                gridref = VcChecker.prepare_sref(sref.gridref)
                VcChecker.check(gridref, code)

        except Exception as e:
            result.ok = False
            result.messages.append(str(e))

        results.append(result)

    return results


@router.post(
    "/records_by_name",
    summary="Validate records identified by name.",
    response_model=list[Validated])
async def validate_by_name(session: DB, records: list[ValidateName]):

    results = []
    return results
