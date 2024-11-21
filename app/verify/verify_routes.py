import time

from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.database import DbDependency
from app.rule.org_group.org_group_repo import OrgGroupRepo
from app.rule.rule_repo import RuleRepo
from app.settings_env import EnvDependency
import app.species.cache as cache
from app.utility.sref.sref_factory import SrefFactory
from app.utility.vague_date import VagueDate

from .verify_models import VerifyPack, Verified, VerifiedPack


router = APIRouter(
    tags=["Verify"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/verify",
    summary="Verify records.",
    response_model=VerifiedPack,
    response_model_exclude_none=True)
async def verify(db: DbDependency, env: EnvDependency, data: VerifyPack):
    """ Verify an array of records against an array of rules.
    If the array of rules is empty, all rules will be run."""

    start = time.time_ns()
    results = []
    for record in data.records:
        # Our response begins with the input data.
        verified = Verified(**record.model_dump())

        # Since we expect valid data, bail out at the first error
        # to save processing time.
        try:
            # 1. Get preferred TVK.
            if not record.tvk and not record.name:
                raise ValueError("TVK or name required.")
            if record.tvk:
                # Use TVK if provided as not ambiguous.
                taxon = cache.get_taxon_by_tvk(db, env, record.tvk)
                if not record.name:
                    verified.name = taxon.name
                elif record.name != taxon.name:
                    raise ValueError(
                        f"Name does not match TVK. Expected {taxon.name}.")
            else:
                # Otherwise use name.
                taxon = cache.get_taxon_by_name(db, env, record.name)
                verified.tvk = taxon.tvk

            verified.preferred_tvk = taxon.preferred_tvk

            # 2. Format date.
            vague_date = VagueDate(record.date)
            verified.date = str(vague_date)

            # 3. Obtain gridref.
            functional_sref = SrefFactory(record.sref)
            verified.sref = functional_sref.value

            # 4. Format stage
            if record.stage is not None:
                verified.stage = record.stage.strip().lower()

            # 5. Look up org_groups and create new list of org_groups & rules.
            new_org_group_rules_list = []
            if data.org_group_rules_list is not None:
                org_group_repo = OrgGroupRepo(db)
                for org_group_rules in data.org_group_rules_list:
                    organisation = org_group_rules.organisation
                    group = org_group_rules.group
                    rules = org_group_rules.rules
                    org_group = org_group_repo.get(organisation, group)
                    if org_group is None:
                        raise ValueError(
                            "Unrecognised organisation:group, "
                            f"'{organisation}:{group}'."
                        )
                    new_org_group_rules_list.append({
                        "org_group": org_group,
                        "rules": rules
                    })

            # 6. Get id difficulty.
            repo = RuleRepo(db, env)
            repo.run_difficulty(new_org_group_rules_list, verified)

            # 7. Check against rules.
            if verified.id_difficulty is not None:
                repo.run_rules(new_org_group_rules_list, verified)

            # Order the messages for clarity and testability.
            verified.messages.sort()

        except (Exception) as e:
            verified.result = 'fail'
            verified.messages.append(str(e))
        finally:
            # Accumulate results.
            results.append(verified)

    duration = time.time_ns() - start

    return VerifiedPack(
        org_group_rules_list=data.org_group_rules_list,
        records=results,
        duration_ns=duration
    )
