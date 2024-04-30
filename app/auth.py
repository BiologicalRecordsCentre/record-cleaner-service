from datetime import datetime, timedelta, timezone
from typing import Annotated, TypeAlias

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.database import DB
from app.settings import settings
from app.sqlmodels import User


# Instantiate a router.
router = APIRouter()

# Instantiate the security provider.
# Set /token as the path to log in.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

authentication_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"}
)
authorization_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You do not have enough permissions for this action.",
    headers={"WWW-Authenticate": "Bearer"}
)


def verify_password(plain_password: str, hashed_password: str | bytes):
    """Confirms a password matches its hashed version."""
    plain_password = plain_password.encode('utf-8')
    if type(hashed_password) is str:
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)


# Hash a password using bcrypt
def hash_password(password: str):
    """Creates a hashed password."""
    password_byte_enc = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_byte_enc, salt)
    return hashed_password


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Creates an access token for a user."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.env.jwt_key,
                             algorithm=settings.env.jwt_algorithm)
    return encoded_jwt


def authenticate_user(session: Session, username: str, password: str):
    """Confirms a username and password match."""
    user = session.exec(
        select(User)
        .where(User.name == username)
    ).one_or_none()
    if not user:
        return False
    if not verify_password(password, user.hash):
        return False
    return user


def get_current_user(
    token:  Annotated[str, Depends(oauth2_scheme)],
    session: DB
):
    """Confirms an access token is valid."""
    try:
        payload = jwt.decode(token, settings.env.jwt_key,
                             algorithms=[settings.env.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise authentication_exception
    except JWTError:
        raise authentication_exception

    user = session.exec(
        select(User)
        .where(User.name == username)
    ).one_or_none()

    if user is None or user.is_disabled:
        raise authentication_exception
    return user


def get_current_admin_user(
    user:  Annotated[User, Depends(get_current_user)]
):
    """Confirms an access token is valid for an admin."""
    if not user.is_admin:
        raise authorization_exception
    return user


# Create a type alias for brevity when defining an endpoint needing
# authentication.
Auth: TypeAlias = Annotated[User, Depends(get_current_user)]
Admin: TypeAlias = Annotated[User, Depends(get_current_admin_user)]


@router.post(
    "/token",
    tags=['Users'],
    summary="Login user.")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DB
):
    # Automatic validation ensures username and password exist.
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise authentication_exception

    access_token_expires = timedelta(minutes=settings.env.jwt_expires_minutes)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
