from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

import app.auth as auth

from . import rules

router = APIRouter()


@router.get(
    "/rules/update",
    tags=['Rules'],
    summary="Updates rules."
)
async def update_rules(token: auth.Auth):

    try:
        commit = rules.update()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))
    else:
        return {"ok": True, "commit": commit}


@router.get(
    "/rules/list",
    tags=['Rules'],
    summary="List rulesets."
)
# async def list_rules(token: auth.Auth):
async def list_rules():
    try:
        result = rules.list_rules()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))
    else:
        return result


@router.get(
    "/rules/id-difficulty/{tvk}",
    tags=['Rules'],
    summary="Get id difficulty by TVK."
)
# async def list_rules(token: auth.Auth):
async def get_id_difficulty(tvk: str):
    try:
        result = ''
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))
    else:
        return result
