from fastapi import APIRouter

from app.database import DbDependency

from .stage_models import StageSynonymResponse
from .stage_repo import StageRepo


router = APIRouter()


@router.get(
    "/stage-synonyms/{org_group_id}",
    summary="List stage synonyms.",
    response_model=list[StageSynonymResponse]
)
async def read_codes(db: DbDependency, org_group_id: int):
    repo = StageRepo(db)
    stages = repo.list(org_group_id)
    return stages
