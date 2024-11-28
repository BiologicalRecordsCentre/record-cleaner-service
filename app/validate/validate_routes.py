
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
    """You must provide **name** or **tvk** (taxon version key) to identify the
    taxon to be checked. **Id**, **date** and a valid **sref** (spatial
    reference) are also required.

    Dates can be supplied in various formats:
    * Single dates as yyyy-mm-dd, d/m/yyyy, d.m.yyyy, d month yyyy, d mon yyyy
    * Single months as yyyy-mm, m/yyyy, m.yyyy, month yyyy, mon yyyy
    * Single years as yyyy
    * Date ranges as yyyy-mm-dd - yyyy-mm-dd, d/m/yyyy - d/m/yyyy,
      d-d/m/yyyy, d/m-d/m/yyyy
    * Month ranges as yyyy-mm - yyyy-mm, m/yyyy - m/yyyy, m-m/yyyy
    * Year ranges as yyyy - yyyy

    They are returned in the preferred format
    * Single dates as dd/mm/yyyy
    * Single months as mm/yyyy
    * Single years as yyyy
    * Date ranges as dd/mm/yyyy - dd/mm/yyyy
    * Month ranges as mm/yyyy - mm/yyyy
    * Year ranges as yyyy - yyyy

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

    The response will contain a grid reference.

    If you supply a British vice county (vc), the sref will be checked to see
    if it might fall within that vice county. This is done by comparing with a
    list of 1km squares and the vice counties that overlap those squares. As
    such, the check is not guaranteed to be correct but eliminates gross
    errors.

    If no vice county is supplied then the response will include a suggested
    Britishvice county which will be the vice county which is predominate in
    the 1km square that the sref falls in.

    The result field in the response will be either pass, warn or fail,
    indicating the outcome of validation. An example of a warning is when a
    location is in the sea and thus not in any vice county. Where there are
    warnings or failures, the message field will contain details of what has
    been detected.

    To avoid server timeouts and database locks,you are advised to submit
    records in modest chunks e.g. 100 records. No limit is currently imposed
    but this may change in future. """

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
