from datetime import datetime, timedelta, timezone
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel

import app.config as config

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": b'$2b$12$g6po0M6AwpbtaWpNSntpteI3HRKUWS.JgKFAyOadvk2PSJ3GYUuYq',
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


# Instantiate a router.
router = APIRouter()

# Instantiate the security provider.
# Set /token as the path to log in.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Load private settings from .env file.
settings = config.get_settings()


# Check if the provided password matches the stored password (hashed)
def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password)


# Hash a password using bcrypt
def hash_password(password):
    password_byte_enc = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_byte_enc, salt)
    return hashed_password


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_key,
                             algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def authenticate(token:  Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_key,
                             algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return True

# Create a type alias for brevity when defining an endpoint needing
# authentication.
Auth: TypeAlias = Annotated[bool, Depends(authenticate)]


@router.post(
    "/token",
    tags=['Users'],
    summary="Login user.")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = fake_users_db.get(form_data.username)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.jwt_expires_minutes)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
