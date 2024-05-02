
from fastapi import APIRouter, HTTPException, status

from app.database import DB

from .tenkm_rule_models import TenkmRuleResponse, TenkmRuleResponseTvk
from .tenkm_rule_repo import TenkmRuleRepo


router = APIRouter()


@router.get(
    "/tenkm-rules/org_group/{org_group_id}",
    summary="List ten km rules for organisation group.",
    response_model=list[TenkmRuleResponse]
)
async def read_rules_by_org_group(session: DB, org_group_id: int):
    repo = TenkmRuleRepo(session)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/tenkm-rules/tvk/{tvk}",
    summary="List tenkm rules for TVK.",
    response_model=list[TenkmRuleResponseTvk]
)
async def read_rules_by_tvk(session: DB, tvk: str):
    repo = TenkmRuleRepo(session)
    rules = repo.list_by_tvk(tvk)
    return rules
