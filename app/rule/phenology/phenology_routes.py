
from fastapi import APIRouter

from app.database import DbDependency
from app.settings_env import EnvDependency
from app.species.cache import get_taxon_by_tvk

from .phenology_models import PhenologyRuleResponse, PhenologyRuleResponseOrganism
from .phenology_repo import PhenologyRuleRepo


router = APIRouter()


@router.get(
    "/phenology/org_group/{org_group_id}",
    summary="List phenology rules for organisation group.",
    response_model=list[PhenologyRuleResponse]
)
async def read_rules_by_org_group(
    db: DbDependency,
    env: EnvDependency,
    org_group_id: int
):
    repo = PhenologyRuleRepo(db, env)
    rules = repo.list_by_org_group(org_group_id)
    return rules


@router.get(
    "/phenology/tvk/{tvk}",
    summary="List phenology rules for TVK.",
    response_model=list[PhenologyRuleResponseOrganism]
)
async def read_rules_by_tvk(db: DbDependency, env: EnvDependency, tvk: str):
    taxon = get_taxon_by_tvk(db, env, tvk)
    repo = PhenologyRuleRepo(db, env)
    rules = repo.list_by_organism_key(taxon.organism_key)
    return rules


@router.get(
    "/phenology/organism_key/{organism_key}",
    summary="List phenology rules for organism key.",
    response_model=list[PhenologyRuleResponseOrganism]
)
async def read_rules_by_organism_key(
    db: DbDependency, env: EnvDependency, organism_key: str
):
    repo = PhenologyRuleRepo(db, env)
    rules = repo.list_by_organism_key(organism_key)
    return rules
