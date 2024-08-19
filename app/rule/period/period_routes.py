
from fastapi import APIRouter

from app.auth import Auth
from app.database import DB


from .period_models import PeriodRuleResponse, PeriodRuleResponseTvk
from .period_repo import PeriodRuleRepo


router = APIRouter(
    prefix="/period",
    tags=['Rules'],
    # dependencies=[Depends(get_current_user)]

)


@router.get(
    "/org_group/{org_group_id}",
    summary="List period rules for organisation group.",
    response_model=list[PeriodRuleResponse]
)
async def read_rules_by_org_group(session: DB, org_group_id: int):
    repo = PeriodRuleRepo(session)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/tvk/{tvk}",
    summary="List period rules for TVK.",
    response_model=list[PeriodRuleResponseTvk]
)
async def read_rules_by_tvk(session: DB, tvk: str):
    repo = PeriodRuleRepo(session)
    rules = repo.list_by_tvk(tvk)
    return rules
