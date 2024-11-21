
from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.database import DbDependency
from app.settings_env import EnvDependency
import app.species.cache as cache
from app.utility.sref.sref_factory import SrefFactory
from app.utility.vice_county.vc_checker import VcChecker, NoVcException
from app.utility.vague_date import VagueDate

from .validate_models import Validate, Validated

router = APIRouter(
    tags=["Validate"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/validate",
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
        validated = Validated(**record.model_dump())

        # As we are validating, try to return as many errors as we can find
        # to save human time.
        try:
            # 1. Confirm TVK/name is valid.
            if not record.tvk and not record.name:
                validated.result = 'fail'
                validated.messages.append("TVK or name required.")
            else:
                if record.tvk:
                    # Use TVK if provided as not ambiguous.
                    taxon = cache.get_taxon_by_tvk(db, env, record.tvk)
                    if not record.name:
                        validated.name = taxon.name
                    elif record.name != taxon.name:
                        validated.result = 'fail'
                        validated.messages.append(
                            f"Name does not match TVK. Expected {taxon.name}.")
                else:
                    # Otherwise use name.
                    taxon = cache.get_taxon_by_name(db, env, record.name)
                    validated.tvk = taxon.tvk

                validated.preferred_tvk = taxon.preferred_tvk

        except Exception as e:
            validated.result = 'fail'
            validated.messages.append(str(e))

        try:
            # 2. Confirm date is valid.
            vague_date = VagueDate(record.date)
            # Return date in preferred format.
            validated.date = str(vague_date)
        except Exception as e:
            validated.result = 'fail'
            validated.messages.append(str(e))

        try:
            # 3. Confirm sref is valid.
            sref = SrefFactory(record.sref)
            # Include gridref in validated.
            validated.sref.gridref = sref.gridref

            # 4a. Either check vice county...
            if record.vc is not None:
                code = VcChecker.prepare_code(record.vc)
                # Return code if name was supplied.
                validated.vc = code
                gridref = VcChecker.prepare_sref(sref.gridref)
                VcChecker.check(gridref, code)
            # 4b. Or assign vice county.
            else:
                gridref = VcChecker.prepare_sref(sref.gridref)
                validated.vc = VcChecker.get_code_from_sref(gridref)

        except NoVcException as e:
            # Failure to assign is a warning but must not override a fail.
            validated.vc = None
            if validated.result == 'pass':
                validated.result = 'warn'
            validated.messages.append(str(e))
        except Exception as e:
            validated.result = 'fail'
            validated.messages.append(str(e))

        results.append(validated)

    return results
