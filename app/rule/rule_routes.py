import json

from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Query, Depends

from app.auth import get_current_user
from app.database import DB
from app.settings import settings

from .rule_repo import RuleRepo

from .additional.additional_routes import router as additional_router
from .stage.stage_routes import router as stage_router
from .difficulty.difficulty_routes import router as difficulty_router
from .org_group.org_group_routes import router as org_group_router
from .period.period_routes import router as period_router
from .phenology.phenology_routes import router as phenology_router
from .tenkm.tenkm_routes import router as tenkm_router

router = APIRouter(
    prefix="/rules",
    tags=['Rules'],
    dependencies=[Depends(get_current_user)]
)
router.include_router(org_group_router)
router.include_router(stage_router)
router.include_router(additional_router)
router.include_router(difficulty_router)
router.include_router(period_router)
router.include_router(phenology_router)
router.include_router(tenkm_router)


@router.get("/update", summary="Updates rules.")
async def update_rules(
    session: DB,
    full: Annotated[
        bool,
        Query(description="Set true to force update from all files. By "
              "default, only changed files are used.")
    ] = False,
):

    try:
        repo = RuleRepo(session)
        response = repo.update(full)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))
    else:
        return response


@router.get("/update_status", summary="Check results of last rule update.")
async def update_status(session: DB):

    if settings.db.rules_updating:
        return {
            'ok': False,
            'data': "Rule update already in progress.",
            'commit': settings.db.rules_commit
        }
    else:
        return json.loads(settings.db.rules_update_result)

# @router.get(
#     "/rulesets",
#     tags=['Rules'],
#     summary="List rulesets."
# )
# async def list_rules(token: auth.Auth):
# async def list_rules():
#     try:
#         result = rule_repo.list_rules()
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e))
#     else:
#         return result


# @router.get(
#     "/rules",
#     tags=['Rules'],
#     summary="List rules.",
#     response_model=list[Rule])
# # async def read_rules(token: auth.Auth):
# async def read_rules():
#     with Session(engine) as session:
#         rules = session.exec(
#             select(Rule).order_by(Rule.organisation, Rule.group, Rule.name)
#         ).all()

#     return rules


# @router.get(
#     "/rules/{tvk}",
#     tags=['Rules'],
#     summary="Get rules by TVK.",
#     response_model=list[Rule])
# async def read_rule(
#         auth: auth.Auth,
#         tvk: str):
#     with Session(engine) as session:
#         rules = session.exec(
#             select(Rule)
#             .where(Rule.preferred_tvk == tvk)
#             .order_by(Rule.organisation, Rule.group, Rule.name)
#         ).all()
#     if len(rules) == 0:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"No rule found for tvk {tvk}.")

#     return rules
