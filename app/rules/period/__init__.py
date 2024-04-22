
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth import Auth
from app.database import DB


from .period_rule_repo import PeriodRuleRepo


router = APIRouter()


class PeriodRuleResponse(BaseModel):
    tvk: str
    taxon: str
    start_date: str
    end_date: str


class PeriodRuleResponseTvk(BaseModel):
    organisation: str
    group: str
    start_date: str
    end_date: str


@router.get(
    "/rules/period-rules/org_group/{org_group_id}",
    tags=['Rules'],
    summary="List period rules for organisation group.",
    response_model=list[PeriodRuleResponse]
)
async def read_rules_by_org_group(
    token: Auth,
    session: DB,
    org_group_id: int
):
    repo = PeriodRuleRepo(session)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/rules/period-rules/tvk/{tvk}",
    tags=['Rules'],
    summary="List period rules for TVK.",
    response_model=list[PeriodRuleResponseTvk]
)
async def read_rules_by_tvk(
    token: Auth,
    session: DB,
    tvk: str
):
    repo = PeriodRuleRepo(session)
    rules = repo.list_by_tvk(tvk)
    return rules
