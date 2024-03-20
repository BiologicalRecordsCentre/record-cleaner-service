from fastapi import APIRouter, HTTPException, status

import app.auth as auth


router = APIRouter()


@router.get(
    "/counties/county_by_code/{code}",
    tags=['Counties'],
    summary="Get county with given code.")
async def read_county_by_code(
        auth: auth.Auth,
        code: str):

    return {"code": code}


@router.get(
    '/counties/county_by_name/{name}',
    tags=['Counties'],
    summary="Get county with given name.",)
async def read_county_by_name(
        auth: auth.Auth,
        name: str):

    return {"name": name}
