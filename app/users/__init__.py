from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select, delete

import app.auth as auth
from app.database import engine
from app.models import User

router = APIRouter()


class UserGet(BaseModel):
    id: int
    name: str


class UserPost(BaseModel):
    name: str
    password: str


class UserPatch(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None


@router.get(
    "/users",
    tags=['Users'],
    summary="List users.",
    response_model=list[UserGet])
async def read_users(
        token: auth.Auth):
    with Session(engine) as session:
        users = session.exec(
            select(User).order_by(User.id)
        ).all()

    return users


@router.get(
    "/user/{id}",
    tags=['Users'],
    summary="Get user.",
    response_model=UserGet)
async def read_user(
        auth: auth.Auth,
        id: int):
    with Session(engine) as session:
        user = session.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with ID {id}.")

    return user


@router.post(
    "/user",
    tags=['Users'],
    summary="Create user.",
    response_model=UserGet)
async def create_user(
        token: auth.Auth,
        user: UserPost):

    hash = auth.hash_password(user.password)
    extra_data = {"hash": hash}

    with Session(engine) as session:
        db_user = User.model_validate(user, update=extra_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


@router.patch(
    "/user/{id}",
    tags=['Users'],
    summary="Update user.",
    response_model=UserGet)
async def update_user(
        auth: auth.Auth,
        id: int,
        user: UserPatch):
    with Session(engine) as session:
        db_user = session.get(User, id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user found with ID {id}.")

        input_data = user.model_dump(exclude_unset=True)
        extra_data = {}
        if 'password' in input_data:
            hash = auth.hash_password(input_data['password'])
            extra_data = {"hash": hash}

        db_user.sqlmodel_update(input_data, update=extra_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    return db_user


@router.delete(
    "/user/{id}",
    tags=['Users'],
    summary="Delete user.")
async def delete_user(
        auth: auth.Auth,
        id: int):
    with Session(engine) as session:
        session.exec(
            delete(User).where(User.id == id)
        )
        session.commit()
    return {"ok": True}
