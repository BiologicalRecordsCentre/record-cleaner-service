from fastapi import APIRouter

from app.database import DbDependency
from app.settings_env import EnvDependency

from .additional_models import (AdditionalCodeResponse, AdditionalRuleResponse,
                                AdditionalRuleResponseTvk)
from .additional_code_repo import AdditionalCodeRepo
from .additional_rule_repo import AdditionalRuleRepo


router = APIRouter()


@router.get(
    "/additional-codes/{org_group_id}",
    summary="List additional codes.",
    response_model=list[AdditionalCodeResponse]
)
async def read_codes(db: DbDependency, env: EnvDependency, org_group_id: int):
    repo = AdditionalCodeRepo(db, env)
    codes = repo.list(org_group_id)
    return codes


@router.get(
    "/additional/org_group/{org_group_id}",
    summary="List additional rules for organisation group.",
    response_model=list[AdditionalRuleResponse]
)
async def read_rules_by_org_group(
    db: DbDependency,
    env: EnvDependency,
    org_group_id: int
):
    repo = AdditionalRuleRepo(db, env)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/additional/tvk/{tvk}",
    summary="List additional rules for TVK.",
    response_model=list[AdditionalRuleResponseTvk]
)
async def read_rules_by_tvk(db: DbDependency, env: EnvDependency, tvk: str):
    repo = AdditionalRuleRepo(db, env)
    rules = repo.list_by_tvk(tvk)
    return rules
