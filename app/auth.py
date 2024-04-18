from datetime import datetime, timedelta, timezone
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import bcrypt

from app.settings import settings

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

# Check if the provided password matches the stored password (hashed)


def verify_password(plain_password, hashed_password):
    """Confirms a password matches its hashed version."""
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password)


# Hash a password using bcrypt
def hash_password(password):
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


async def authenticate(token:  Annotated[str, Depends(oauth2_scheme)]):
    """Confirms an access token is valid."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.env.jwt_key,
                             algorithms=[settings.env.jwt_algorithm])
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
    # Automatic validation ensures username and password exist.
    user = fake_users_db.get(form_data.username)

    access_token_expires = timedelta(minutes=settings.env.jwt_expires_minutes)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
