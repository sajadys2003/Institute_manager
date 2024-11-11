from datetime import datetime, timedelta
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from jwt.exceptions import InvalidTokenError
from app.dependencies import SessionDep
from app.models import User
from sqlalchemy import and_

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: SessionDep, username: str, password: str) -> User:
    criteria = and_(User.phone_number == username, User.is_enabled)
    user = db.query(User).where(criteria).scalar()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return user


def create_token(sub: str):
    payload = {
        "sub": sub,
        "exp": datetime.now() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="bearer")


@router.post("/token")
async def login_for_access_token(
        db: SessionDep,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    authenticated_user = authenticate_user(db, form_data.username, form_data.password)

    if authenticated_user:
        token = create_token(
            sub=authenticated_user.phone_number
        )
        return token


async def get_current_user(
        db: SessionDep,
        token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload["sub"]
        criteria = and_(User.phone_number == username, User.is_enabled)
        user = db.query(User).where(criteria).scalar()
        if not user:
            raise credentials_exception

    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    return user


CurrentUer = Annotated[User, Depends(get_current_user)]


def authorized(
        current_user: User,
        operation: str
) -> User:
    if not current_user.is_super_admin:

        permissions_list = current_user.permissions_list
        if not permissions_list or operation not in permissions_list:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions"
            )
    return current_user
