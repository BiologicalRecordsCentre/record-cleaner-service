
from fastapi import APIRouter, HTTPException, status, Depends

from app.auth import get_current_user
from app.database import DbDependency

from .org_group_models import OrgGroupResponse
from .org_group_repo import OrgGroupRepo, OrgGroup


router = APIRouter()


@router.get(
    "/org-groups",
    summary="List of organisations and groups.",
    response_model=list[OrgGroupResponse],
    dependencies=[Depends(get_current_user)],
)
async def list(db: DbDependency):
    repo = OrgGroupRepo(db)
    return repo.list()


@router.get(
    "/org-groups/{id}",
    summary="Details of organisation group.",
    response_model=OrgGroup
)
async def list(db: DbDependency, id: int):
    repo = OrgGroupRepo(db)
    org_group = repo.list(id)
    if org_group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No item found with ID {id}.")
    return org_group
