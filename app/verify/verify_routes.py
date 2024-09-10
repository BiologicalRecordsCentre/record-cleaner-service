
from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.database import DB
from app.rule.rule_repo import RuleRepo
import app.species.cache as cache
from app.utility.sref.sref_factory import SrefFactory
from app.utility.vague_date import VagueDate

from .verify_models import VerifyPack, Verified, VerifiedPack


router = APIRouter(
    prefix="/verify",
    tags=["Verify"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/",
    summary="Verify records.",
    response_model=VerifiedPack,
    response_model_exclude_none=True)
async def verify(session: DB, data: VerifyPack):

    results = []
    for record in data.records:
        # Our response begins with the input data.
        result = Verified(**record.model_dump())

        try:
            # 1. Get preferred TVK.
            if record.tvk is not None:
                # Use TVK if provided as not ambiguous.
                taxon = cache.get_taxon_by_tvk(session, record.tvk)
                if record.name is None:
                    result.name = taxon.name
                elif record.name != taxon.name:
                    result.ok = False
                    result.messages.append(
                        f"Name does not match TVK. Expected {taxon.name}.")
            elif record.name is not None:
                # Otherwise use name.
                taxon = cache.get_taxon_by_name(session, record.name)
                if record.tvk is None:
                    result.tvk = taxon.tvk

            result.preferred_tvk = taxon.preferred_tvk

            # 2. Format date.
            vague_date = VagueDate(record.date)
            result.date = str(vague_date)

            # 3. Obtain gridref.
            functional_sref = SrefFactory(record.sref)
            result.sref = functional_sref.value

            # 4. Format stage
            if record.stage is not None:
                result.stage = record.stage.strip().lower()

            # 5. Check against rules.
            repo = RuleRepo(session)
            repo.run_rules(data.org_group_rules_list, result)

            # Accumulate results.
            results.append(result)

        except (Exception) as e:
            result.ok = False
            result.messages.append(str(e))
            results.append(result)
            continue

    return VerifiedPack(
        org_group_rules_list=data.org_group_rules_list,
        records=results
    )
