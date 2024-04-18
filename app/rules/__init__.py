import app.rules.rules as rules
from .difficulty import router as difficulty_router
from .org_group import router as org_group_router
from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select


import app.auth as auth
from app.database import engine
# from app.sqlmodels import Rule


router = APIRouter()
router.include_router(difficulty_router)
router.include_router(org_group_router)


@router.get(
    "/rules/update",
    tags=['Rules'],
    summary="Updates rules."
)
async def update_rules(token: auth.Auth):

    try:
        commit = rules.update()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))
    else:
        return {"ok": True, "commit": commit}


@router.get(
    "/rulesets",
    tags=['Rules'],
    summary="List rulesets."
)
# async def list_rules(token: auth.Auth):
async def list_rules():
    try:
        result = rules.list_rules()
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


@router.get(
    "/rules/id-difficulty/{tvk}",
    tags=['Rules'],
    summary="Get id difficulty by TVK."
)
# async def list_rules(token: auth.Auth):
async def get_id_difficulty(tvk: str):
    try:
        result = ''
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e))
    else:
        return result
