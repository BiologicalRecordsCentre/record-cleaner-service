from .rule_repo import RuleRepo

from .additional import router as additional_router
from .difficulty import router as difficulty_router
from .org_group import router as org_group_router
from .period import router as period_router
from .tenkm import router as tenkm_router

from fastapi import APIRouter, HTTPException, status

from app.auth import Auth
from app.database import DB


router = APIRouter()
router.include_router(org_group_router)
router.include_router(additional_router)
router.include_router(difficulty_router)
router.include_router(period_router)
router.include_router(tenkm_router)


@router.get(
    "/rules/update",
    tags=['Rules'],
    summary="Updates rules."
)
async def update_rules(token: Auth, session: DB):

    try:
        repo = RuleRepo(session)
        response = repo.update()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))
    else:
        return response


@router.get(
    "/rulesets",
    tags=['Rules'],
    summary="List rulesets."
)
# async def list_rules(token: auth.Auth):
async def list_rules():
    try:
        result = rule_repo.list_rules()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))
    else:
        return result


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
