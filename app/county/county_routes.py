from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.utility.vice_county.vc_checker import VcChecker


router = APIRouter()
router = APIRouter(
    prefix="/county",
    tags=["Counties"],
    dependencies=[Depends(get_current_user)]
)


@router.get(
    "/code/{code}",
    summary="Get county with given code.")
async def read_county_by_code(code: str | int):

    try:
        code = VcChecker.prepare_code(code)
        return {
            "code": code,
            "name": VcChecker.get_name_from_code(code)
        }
    except ValueError:
        raise HTTPException(
            status_code=404, detail="No county found for code.")


@router.get(
    '/gridref/{gridref}',
    summary="Get county containing gridref.")
async def read_county_by_gridref(gridref: str):
    """Returns the primary county for the gridref but may be incorrect when the
    square straddles more than one county. The gridref must be well formed with
    capital letters and no spaces."""

    try:
        gridref = VcChecker.prepare_sref(gridref)
        code = VcChecker.get_code_from_sref(gridref)
        return {
            "gridref": gridref,
            "code": code,
            "name": VcChecker.get_name_from_code(code)
        }
    except ValueError:
        raise HTTPException(
            status_code=404, detail="No county found for gridref.")
