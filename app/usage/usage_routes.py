from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import select, func

from app.auth import get_current_admin_user
from app.database import DbDependency
from app.sqlmodels import Usage

# Must be an admin user to access these routes.
router = APIRouter(
    prefix="/usage",
    tags=["Usage"],
    dependencies=[Depends(get_current_admin_user)]
)


class UsageBase(BaseModel):
    verification_requests: int
    validation_requests: int
    verification_records: int
    validation_records: int


class UsageName(UsageBase):
    user_name: str


class UsageYear(UsageBase):
    year: int


class UsageMonth(UsageBase):
    month: int


@router.get(
    '/user/{username}',
    summary="List usage for given user by year.",
    response_model=list[UsageYear]
)
async def get_usage_by_year(db: DbDependency, username: str):
    """Get usage for given user by year."""
    usages = db.exec(
        select(
            Usage.year,
            func.sum(Usage.verification_requests),
            func.sum(Usage.validation_requests),
            func.sum(Usage.verification_records),
            func.sum(Usage.validation_records)
        ).
        where(Usage.user_name == username).
        group_by(Usage.year).
        order_by(Usage.year)
    ).all()

    # Convert database output to a list of UsageGet.
    response = []
    for usage in usages:
        response.append(Usage(
            year=usage[0],
            verification_requests=usage[1],
            validation_requests=usage[2],
            verification_records=usage[3],
            validation_records=usage[4]
        ))

    return response


@router.get(
    '/user/{username}/{year}',
    summary="List usage for given user and year by month.",
    response_model=list[UsageMonth]
)
async def get_usage_by_month(db: DbDependency, username: str, year: int):
    """Get usage for given user and year by month."""
    usages = db.exec(
        select(Usage).
        where(Usage.user_name == username).
        where(Usage.year == year).
        order_by(Usage.month)
    ).all()

    return usages


@router.get(
    '/{year}',
    summary="List all usage for given year.",
    response_model=list[UsageName]
)
async def get_all_usage_for_year(db: DbDependency, year: int):
    """Get usage for all users in the given year."""
    usages = db.exec(
        select(
            Usage.user_name,
            func.sum(Usage.verification_requests),
            func.sum(Usage.validation_requests),
            func.sum(Usage.verification_records),
            func.sum(Usage.validation_records)
        ).
        where(Usage.year == year).
        group_by(Usage.user_name).
        order_by(Usage.user_name)
    ).all()

    # Convert database output to a list of UsageGet.
    response = []
    for usage in usages:
        response.append(UsageName(
            user_name=usage[0],
            verification_requests=usage[1],
            validation_requests=usage[2],
            verification_records=usage[3],
            validation_records=usage[4]
        ))

    return response


@router.get(
    '/{year}/{month}',
    summary="List all usage for given year and month.",
    response_model=list[UsageName]
)
async def get_all_usage_for_year_month(db: DbDependency, year: int, month: int):
    """Get usage for all users in the given month and year."""
    usages = db.exec(
        select(Usage).
        where(Usage.year == year).
        where(Usage.month == month).
        order_by(Usage.user_name)
    ).all()

    return usages
