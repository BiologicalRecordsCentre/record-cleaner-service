
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth import Auth
from app.database import DB

from .additional_code_repo import AdditionalCodeRepo
from .additional_rule_repo import AdditionalRuleRepo


router = APIRouter()


class AdditionalCodeResponse(BaseModel):
    code: int
    text: str


class AdditionalRuleResponse(BaseModel):
    tvk: str
    taxon: str
    code: int


class AdditionalRuleResponseTvk(BaseModel):
    organisation: str
    group: str
    code: int
    text: str


@router.get(
    "/rules/additional-codes/{org_group_id}",
    tags=['Rules'],
    summary="List additional codes.",
    response_model=list[AdditionalCodeResponse]
)
# async def read_rules(token: auth.Auth):
async def read_codes(
    token: Auth,
    session: DB,
    org_group_id: int
):
    repo = AdditionalCodeRepo(session)
    codes = repo.list(org_group_id)
    return codes


@router.get(
    "/rules/additional-rules/org_group/{org_group_id}",
    tags=['Rules'],
    summary="List additional rules for organisation group.",
    response_model=list[AdditionalRuleResponse]
)
async def read_rules_by_org_group(
    token: Auth,
    session: DB,
    org_group_id: int
):
    repo = AdditionalRuleRepo(session)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/rules/additional-rules/tvk/{tvk}",
    tags=['Rules'],
    summary="List additional rules for TVK.",
    response_model=list[AdditionalRuleResponseTvk]
)
async def read_rules_by_tvk(
    token: Auth,
    session: DB,
    tvk: str
):
    repo = AdditionalRuleRepo(session)
    rules = repo.list_by_tvk(tvk)
    return rules
