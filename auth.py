import base64
import hashlib
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, timezone, datetime
import exceptions
import models
import settings
import jwt
import hmac

SECRET = settings.SECRET
DIGEST = 'sha256'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


async def get_user(username: str):
    return await models.User.objects.get_or_none(username=username)


def create_password_hash(password: str):
    secret = hashlib.sha256(settings.SECRET.encode()).digest()
    secret = base64.urlsafe_b64encode(secret)
    new_hash = hashlib.sha512(secret + password.encode()).hexdigest()
    return new_hash


def verify_password(plain_password: str, hashed_password: str):
    new_hash = create_password_hash(plain_password)
    return hmac.compare_digest(new_hash, hashed_password)


async def authenticate_user(username: str, password: str):
    user = await get_user(username=username)
    if not user:
        return False

    if not verify_password(password, user.password):
        return False

    return user


def create_access_token(user: dict, data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET,
        algorithm=ALGORITHM,
        headers=dict(user=user)
    )
    return encoded_jwt


def check_user_auth(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise exceptions.INCORRECT_LOGIN_DATA_EXCEPTION

    except jwt.exceptions.PyJWTError as error:
        raise exceptions.INCORRECT_LOGIN_DATA_EXCEPTION

    return username


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    username = check_user_auth(token)

    user = await get_user(username=username)
    if user is None:
        raise exceptions.INCORRECT_LOGIN_DATA_EXCEPTION

    return user


def create_token(user: models.User):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": user.username}
    access_token = create_access_token(
        user=user.model_dump(exclude={'date_joined'}),
        data=data,
        expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'Bearer'}


UserType = Annotated[models.User, Depends(get_current_user)]

