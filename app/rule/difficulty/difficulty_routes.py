
from fastapi import APIRouter

from app.database import DbDependency
from app.settings_env import EnvDependency

from .difficulty_code_repo import DifficultyCodeRepo
from .difficulty_rule_repo import DifficultyRuleRepo
from .difficulty_models import DifficultyCodeResponse, DifficultyRuleResponse, DifficultyRuleResponseTvk


router = APIRouter()


@router.get(
    "/difficulty-codes/{org_group_id}",
    summary="List difficulty codes.",
    response_model=list[DifficultyCodeResponse]
)
async def read_codes(db: DbDependency, env: EnvDependency, org_group_id: int):
    repo = DifficultyCodeRepo(db, env)
    codes = repo.list(org_group_id)
    return codes


@router.get(
    "/difficulty/org_group/{org_group_id}",
    summary="List difficulty rules for organisation group.",
    response_model=list[DifficultyRuleResponse]
)
async def read_rules_by_org_group(
    db: DbDependency,
    env: EnvDependency,
    org_group_id: int
):
    repo = DifficultyRuleRepo(db, env)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/difficulty/tvk/{tvk}",
    summary="List difficulty rules for TVK.",
    response_model=list[DifficultyRuleResponseTvk]
)
async def read_rules_by_tvk(db: DbDependency, env: EnvDependency, tvk: str):
    repo = DifficultyRuleRepo(db, env)
    rules = repo.list_by_tvk(tvk)
    return rules
