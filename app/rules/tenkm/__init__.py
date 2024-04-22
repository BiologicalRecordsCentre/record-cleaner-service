
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth import Auth
from app.database import DB


from .tenkm_rule_repo import TenkmRuleRepo


router = APIRouter()


class TenkmRuleResponse(BaseModel):
    tvk: str
    taxon: str
    km100: str
    km10: str
    coord_system: str


class TenkmRuleResponseTvk(BaseModel):
    organisation: str
    group: str
    km100: str
    km10: str
    coord_system: str


@router.get(
    "/rules/tenkm-rules/org_group/{org_group_id}",
    tags=['Rules'],
    summary="List ten km rules for organisation group.",
    response_model=list[TenkmRuleResponse]
)
async def read_rules_by_org_group(
    token: Auth,
    session: DB,
    org_group_id: int
):
    repo = TenkmRuleRepo(session)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/rules/tenkm-rules/tvk/{tvk}",
    tags=['Rules'],
    summary="List tenkm rules for TVK.",
    response_model=list[TenkmRuleResponseTvk]
)
async def read_rules_by_tvk(
    token: Auth,
    session: DB,
    tvk: str
):
    repo = TenkmRuleRepo(session)
    rules = repo.list_by_tvk(tvk)
    return rules
