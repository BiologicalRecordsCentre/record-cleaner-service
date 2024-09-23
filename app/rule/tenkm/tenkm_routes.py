
from fastapi import APIRouter, HTTPException, status

from app.database import DbDependency
from app.settings_env import EnvDependency

from .tenkm_models import TenkmRuleResponse, TenkmRuleResponseTvk
from .tenkm_repo import TenkmRuleRepo


router = APIRouter()


@router.get(
    "/tenkm/org_group/{org_group_id}",
    summary="List ten km rules for organisation group.",
    response_model=list[TenkmRuleResponse]
)
async def read_rules_by_org_group(
    db: DbDependency, env: EnvDependency, org_group_id: int
):
    repo = TenkmRuleRepo(db, env)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/tenkm/tvk/{tvk}",
    summary="List tenkm rules for TVK.",
    response_model=list[TenkmRuleResponseTvk]
)
async def read_rules_by_tvk(db: DbDependency, env: EnvDependency, tvk: str):
    repo = TenkmRuleRepo(db, env)
    rules = repo.list_by_tvk(tvk)
    return rules
