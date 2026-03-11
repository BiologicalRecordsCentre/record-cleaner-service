
from fastapi import APIRouter, HTTPException, status

from app.database import DbDependency
from app.settings_env import EnvDependency
from app.species.cache import get_taxon_by_tvk

from .period_models import PeriodRuleResponse, PeriodRuleResponseOrganism
from .period_repo import PeriodRuleRepo


router = APIRouter()


@router.get(
    "/period/org_group/{org_group_id}",
    summary="List period rules for organisation group.",
    response_model=list[PeriodRuleResponse]
)
async def read_rules_by_org_group(
    db: DbDependency,
    env: EnvDependency,
    org_group_id: int
):
    repo = PeriodRuleRepo(db, env)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/period/tvk/{tvk}",
    summary="List period rules for TVK.",
    response_model=list[PeriodRuleResponseOrganism]
)
async def read_rules_by_tvk(db: DbDependency, env: EnvDependency, tvk: str):
    try:
        taxon = get_taxon_by_tvk(db, env, tvk)
        repo = PeriodRuleRepo(db, env)
        rules = repo.list_by_organism_key(taxon.organism_key)
        return rules
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))


@router.get(
    "/period/organism_key/{organism_key}",
    summary="List period rules for organism key.",
    response_model=list[PeriodRuleResponseOrganism]
)
async def read_rules_by_organism_key(
    db: DbDependency, env: EnvDependency, organism_key: str
):
    repo = PeriodRuleRepo(db, env)
    rules = repo.list_by_organism_key(organism_key)
    return rules
