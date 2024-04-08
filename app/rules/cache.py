from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, func, select, delete

from app.database import engine
import app.auth as auth
from app.models import Rule

router = APIRouter()


@router.get(
    "/rules/cache/create",
    tags=['Rules Cache'],
    summary="Build the rules cache from csv files.",
    response_model=int)
async def cache_create(auth: auth.Auth):
    return {"ok": True}


@router.delete(
    "/rules/cache/all",
    tags=['Rules Cache'],
    summary="Empty the rules cache.",
    response_model=bool)
async def cache_clear(auth: auth.Auth):
    with Session(engine) as session:
        session.exec(
            delete(Rule)
        )
        session.commit()
    return {"ok": True}
