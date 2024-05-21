from fastapi import APIRouter, HTTPException, status

from app.database import DB

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
async def read_codes(session: DB, org_group_id: int):
    repo = AdditionalCodeRepo(session)
    codes = repo.list(org_group_id)
    return codes


@router.get(
    "/additional-rules/org_group/{org_group_id}",
    summary="List additional rules for organisation group.",
    response_model=list[AdditionalRuleResponse]
)
async def read_rules_by_org_group(session: DB, org_group_id: int):
    repo = AdditionalRuleRepo(session)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/additional-rules/tvk/{tvk}",
    summary="List additional rules for TVK.",
    response_model=list[AdditionalRuleResponseTvk]
)
async def read_rules_by_tvk(session: DB, tvk: str):
    repo = AdditionalRuleRepo(session)
    rules = repo.list_by_tvk(tvk)
    return rules
