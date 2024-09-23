
from fastapi import APIRouter

from app.database import DbDependency
from app.settings_env import EnvDependency

from .phenology_models import PhenologyRuleResponse, PhenologyRuleResponseTvk
from .phenology_repo import PhenologyRuleRepo


router = APIRouter()


@router.get(
    "/phenology/org_group/{org_group_id}",
    summary="List phenology rules for organisation group.",
    response_model=list[PhenologyRuleResponse]
)
async def read_rules_by_org_group(
    db: DbDependency,
    env: EnvDependency,
    org_group_id: int
):
    repo = PhenologyRuleRepo(db, env)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/phenology/tvk/{tvk}",
    summary="List phenology rules for TVK.",
    response_model=list[PhenologyRuleResponseTvk]
)
async def read_rules_by_tvk(db: DbDependency, env: EnvDependency, tvk: str):
    repo = PhenologyRuleRepo(db, env)
    rules = repo.list_by_tvk(tvk)
    return rules
