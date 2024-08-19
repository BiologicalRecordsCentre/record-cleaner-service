from fastapi import APIRouter

import app.auth as auth
from app.utility.vice_county.vc_checker import VcChecker


router = APIRouter()


@router.get(
    "/counties/county_by_code/{code}",
    tags=['Counties'],
    summary="Get county with given code.")
async def read_county_by_code(
        auth: auth.Auth,
        code: str | int):

    return {
        "code": code,
        "county": VcChecker.prepare_code(code)
    }


@router.get(
    '/counties/county_by_name/{name}',
    tags=['Counties'],
    summary="Get county with given name.",)
async def read_county_by_name(
        auth: auth.Auth,
        name: str):

    return {
        "code": VcChecker.prepare_code(name),
        "county": name
    }
