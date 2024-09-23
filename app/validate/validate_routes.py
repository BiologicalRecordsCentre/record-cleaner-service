
from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.database import DbDependency
from app.rule.difficulty.difficulty_rule_repo import DifficultyRuleRepo
from app.settings_env import EnvDependency
import app.species.cache as cache
from app.utility.sref.sref_factory import SrefFactory
from app.utility.vice_county.vc_checker import VcChecker
from app.utility.vague_date import VagueDate

from .validate_models import Validate, Validated

router = APIRouter(
    prefix="/validate",
    tags=["Validate"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/",
    summary="Validate records.",
    response_model=list[Validated],
    response_model_exclude_none=True)
async def validate(
    db: DbDependency,
    env: EnvDependency,
    records: list[Validate]
):
    """You must provide a name or TVK to identify the taxon to be checked.
    Id, date and a valid sref are also required.

    The spatial reference can be given as a grid reference, a latitude and
    longitude or an easting and northing. In the latter two cases, an accuracy
    is also required. The srid parameter must match the spatial reference 
    system in which the coordinates are given.

    Supported systems are:
    * 27700, The British National Grid
    * 29903, The Irish National Grid
    * 23030, Channel Islands Grid (WV/WA)
    * 0, Automatically select from above 3 grids.
    * 4326, WGS84 latitude/longitude
"""

    results = []
    for record in records:
        # Our response begins with the input data.
        result = Validated(**record.model_dump())

        # 1. Confirm TVK/name is valid.
        try:
            if record.tvk is None and record.name is None:
                result.ok = False
                result.messages.append("TVK or name required.")
            else:
                if record.tvk is not None:
                    # Use TVK if provided as not ambiguous.
                    taxon = cache.get_taxon_by_tvk(db, env, record.tvk)
                    if record.name is None:
                        result.name = taxon.name
                    elif record.name != taxon.name:
                        result.ok = False
                        result.messages.append(
                            f"Name does not match TVK. Expected {taxon.name}.")
                elif record.name is not None:
                    # Otherwise use name.
                    taxon = cache.get_taxon_by_name(db, env, record.name)
                    result.tvk = taxon.tvk

                result.preferred_tvk = taxon.preferred_tvk
                # Get id difficulty.
                repo = DifficultyRuleRepo(db, env)
                result.id_difficulty = repo.run(result)

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
