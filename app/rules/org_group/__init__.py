
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

import app.auth as auth

from .org_group_repo import OrgGroupRepo, OrgGroup


router = APIRouter()


class OrgGroupResponse(BaseModel):
    id: int
    organisation: str
    group: str


@router.get(
    "/rules/org-groups",
    tags=['Rules'],
    summary="List of organisations and groups.",
    response_model=list[OrgGroupResponse])
# async def read_rules(token: auth.Auth):
async def list():
    return OrgGroupRepo.list()


@router.get(
    "/rules/org-groups/{id}",
    tags=['Rules'],
    summary="Details of organisation group.",
    response_model=OrgGroup)
# async def read_rules(token: auth.Auth):
async def list(id: int):
    org_group = OrgGroupRepo.list(id)
    if org_group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No item found with ID {id}.")
    return org_group
