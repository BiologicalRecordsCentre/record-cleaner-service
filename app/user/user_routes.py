from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlmodel import select

from app.auth import hash_password, get_current_admin_user, Auth
from app.database import DbDependency
from app.settings_env import EnvDependency
from app.sqlmodels import User

from .user_repo import UserRepo

# Must be an admin user to access these routes.
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


@router.get('', summary="List users.", response_model=list[UserGet])
async def read_users(db: DbDependency):
    """Get all users."""
    users = db.exec(
        select(User).order_by(User.name)
    ).all()

    return users


@router.get('/me', summary="Get logged in user.", response_model=UserGet)
async def login(user: Auth):
    return user


@router.get('/{username}', summary="Get user.", response_model=UserGet)
async def read_user(db: DbDependency, username: str):
    """Get a single user."""
    user = db.get(User, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with name {username}.")

    return user


@router.post('', summary="Create user.", response_model=UserGet)
async def create_user(db: DbDependency, user_in: UserPost):
    """Add a user account for every consumer of this service.

    * **name** should identify the consumer.
    * **email** should be a valid email address for contacting the consumer.
    * **password** should be set for the consumer.
    * **is_admin** should be set True for the few users who will administer
      the service.
    * **is_disabled** should be set True to disable an account.

    There is a built-in administrative user that can be configured in the 
    host environment.
    """
    repo = UserRepo(db)
    return repo.create_user(user_in)


@router.patch("/{username}",  summary="Update user.", response_model=UserGet)
async def update_user(
    db: DbDependency,
    env: EnvDependency,
    username: str,
    user_in: UserPatch
):
    """Update user with the given name."""
    db_user = db.get(User, username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with name {username}."
        )
    if username == env.initial_user_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {env.initial_user_name} cannot be modified."
        )

    user_in_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if user_in.password:
        hash = hash_password(user_in.password)
        extra_data = {"hash": hash}

    db_user.sqlmodel_update(user_in_data, update=extra_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.delete("/{username}", summary="Delete user.")
async def delete_user(db: DbDependency, env: EnvDependency, username: str):
    """Delete user with the given name."""
    db_user = db.get(User, username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with name {username}."
        )
    if username == env.initial_user_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {env.initial_user_name} cannot be deleted."
        )
    db.delete(db_user)
    db.commit()
    return {"ok": True}
