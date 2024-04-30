from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlmodel import select, delete

from app.auth import hash_password, get_current_admin_user, Auth
from app.database import DB
from app.sqlmodels import User

from .user_repo import UserRepo

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_admin_user)]
)


class UserGet(BaseModel):
    name: str
    email: str
    is_admin: bool
    is_disabled: bool


class UserPost(BaseModel):
    name: str
    email: str
    password: str
    is_admin: bool
    is_disabled: bool


class UserPatch(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    is_disabled: Optional[bool] = None


@router.get('/', summary="List users.", response_model=list[UserGet])
async def read_users(session: DB):
    """Get all users."""
    users = session.exec(
        select(User).order_by(User.name)
    ).all()

    return users


@router.get('/{username}', summary="Get user.", response_model=UserGet)
async def read_user(session: DB, username: str):
    """Get a single user."""
    user = session.get(User, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with name {username}.")

    return user


@router.get('/me', summary="Get logged in user.", response_model=UserGet)
async def login(user: Auth):
    return user


@router.post('/', summary="Create user.", response_model=UserGet)
async def create_user(session: DB, user_in: UserPost):
    """Create a new user."""
    repo = UserRepo(session)
    return repo.create_user(user_in)


@router.patch("/{username}",  summary="Update user.", response_model=UserGet)
async def update_user(session: DB, username: str, user_in: UserPatch):
    """Update user with the given name."""
    db_user = session.get(User, username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with name {username}.")

    user_in_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if user_in.password:
        hash = hash_password(user_in.password)
        extra_data = {"hash": hash}

    db_user.sqlmodel_update(user_in_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.delete("/{username}", summary="Delete user.")
async def delete_user(session: DB, username: str):
    """Delete user with the given name."""
    session.exec(
        delete(User).where(User.name == username)
    )
    session.commit()
    return {"ok": True}
