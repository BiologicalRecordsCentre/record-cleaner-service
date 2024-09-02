from fastapi import APIRouter, Depends

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
async def read_county_by_code( code: str | int):

    return {
        "code": code,
        "county": VcChecker.prepare_code(code)
    }


@router.get(
    '/name/{name}',
    summary="Get county with given name.",)
async def read_county_by_name(name: str):

    return {
        "code": VcChecker.prepare_code(name),
        "county": name
    }
