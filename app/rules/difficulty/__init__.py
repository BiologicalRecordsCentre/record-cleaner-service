
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth import Auth
from app.database import DB

from .difficulty_code_repo import DifficultyCodeRepo
from .difficulty_rule_repo import DifficultyRuleRepo


router = APIRouter()


class DifficultyCodeResponse(BaseModel):
    difficulty: int
    text: str


class DifficultyRuleResponse(BaseModel):
    tvk: str
    taxon: str
    difficulty: int


class DifficultyRuleResponseTvk(BaseModel):
    organisation: str
    group: str
    difficulty: int
    text: str


@router.get(
    "/rules/difficulty-codes/{org_group_id}",
    tags=['Rules'],
    summary="List difficulty codes.",
    response_model=list[DifficultyCodeResponse]
)
# async def read_rules(token: auth.Auth):
async def read_codes(
    token: Auth,
    session: DB,
    org_group_id: int
):
    repo = DifficultyCodeRepo(session)
    codes = repo.list(org_group_id)
    return codes


@router.get(
    "/rules/difficulty-rules/org_group/{org_group_id}",
    tags=['Rules'],
    summary="List difficulty rules for organisation group.",
    response_model=list[DifficultyRuleResponse]
)
async def read_rules_by_org_group(
    token: Auth,
    session: DB,
    org_group_id: int
):
    repo = DifficultyRuleRepo(session)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/rules/difficulty-rules/tvk/{tvk}",
    tags=['Rules'],
    summary="List difficulty rules for TVK.",
    response_model=list[DifficultyRuleResponseTvk]
)
async def read_rules_by_tvk(
    token: Auth,
    session: DB,
    tvk: str
):
    repo = DifficultyRuleRepo(session)
    rules = repo.list_by_tvk(tvk)
    return rules
