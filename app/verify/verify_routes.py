
from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.database import DB
from app.rules.rule_repo import RuleRepo
import app.species.cache as cache
from app.utilities.srefs.sref_factory import SrefFactory
from app.utilities.vague_dates import VagueDate

from .verify_models import VerifyPackTvk, VerifyPackName, Verified, VerifiedPack


router = APIRouter(
    prefix="/verify",
    tags=["Verify"],
    # dependencies=[Depends(get_current_user)]
)


@router.post(
    "/records_by_tvk",
    summary="Verify records identified by TVK.",
    response_model=VerifiedPack)
async def verify_by_tvk(session: DB, data: VerifyPackTvk):

    results = []
    for record in data.records:
        # Our response begins with the input data.
        result = Verified(**record.model_dump())

        try:
            # 1. Get preferred TVK.
            taxon = cache.get_taxon_by_tvk(session, record.tvk)
            result.tvk = taxon.preferred_tvk
            result.name = taxon.preferred_name

            # 2. Format date.
            vague_date = VagueDate(record.date)
            result.date = str(vague_date)

            # 3. Obtain gridref.
            sref = SrefFactory(record.sref)
            result.sref = sref.props()

            # 4. Check against rules.
            repo = RuleRepo(session)
            repo.run_rules(data.org_group_rules_list, result)

            # Accumulate results.
            results.append(result)

        except ValueError as e:
            result.ok = False
            result.message = str(e)
            results.append(result)
            continue

    return VerifiedPack(
        org_group_rules_list=data.org_group_rules_list,
        records=results
    )


@router.post(
    "/records_by_name",
    summary="Verify records identified by name.",
    response_model=list[Verified])
async def verify_by_name(records: list[VerifyPackName]):

    results = []
    return results
