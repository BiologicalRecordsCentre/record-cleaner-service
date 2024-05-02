
from fastapi import APIRouter, HTTPException, status

from app.database import DB

from .difficulty_code_repo import DifficultyCodeRepo
from .difficulty_rule_repo import DifficultyRuleRepo
from .difficulty_models import DifficultyCodeResponse, DifficultyRuleResponse, DifficultyRuleResponseTvk


router = APIRouter()


@router.get(
    "/difficulty-codes/{org_group_id}",
    summary="List difficulty codes.",
    response_model=list[DifficultyCodeResponse]
)
# async def read_rules(token: auth.Auth):
async def read_codes(session: DB, org_group_id: int):
    repo = DifficultyCodeRepo(session)
    codes = repo.list(org_group_id)
    return codes


@router.get(
    "/difficulty-rules/org_group/{org_group_id}",
    summary="List difficulty rules for organisation group.",
    response_model=list[DifficultyRuleResponse]
)
async def read_rules_by_org_group(session: DB, org_group_id: int):
    repo = DifficultyRuleRepo(session)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/difficulty-rules/tvk/{tvk}",
    summary="List difficulty rules for TVK.",
    response_model=list[DifficultyRuleResponseTvk]
)
async def read_rules_by_tvk(session: DB, tvk: str):
    repo = DifficultyRuleRepo(session)
    rules = repo.list_by_tvk(tvk)
    return rules
