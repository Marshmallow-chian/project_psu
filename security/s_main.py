from datetime import datetime, timedelta
from typing import Optional, Union, Literal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from security.s_scheme import Token, TokenData
from app.scheme import UserInDB
from pony.orm import db_session
from app.models import User

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):  # проверяет правильность пароля, True/False
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):  # хэширует пароль
    return pwd_context.hash(password)


def get_user(user_name: str) -> Union[UserInDB, str]:  # ------------
    with db_session:
        if User.exists(nickname=user_name):  # если юзер есть в бд, то выводим его
            user = User.get(nickname=user_name)
            return UserInDB.from_orm(user)
        else:
            return 'пользователя с таким id не существует'


def authenticate_user(username: str, password: str) -> Union[UserInDB, Literal[False]]:  # --------------
    user = get_user(username)
    if isinstance(user, str):
        return False
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):  # ставит метку
    from app.main import SECRET_KEY

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    from app.main import SECRET_KEY

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(name=username)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.name)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):  # UserInDB
    return current_user
