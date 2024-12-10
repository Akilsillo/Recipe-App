from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from typing import Annotated
from jose import jwt, JWTError
from .core import settings
from schemas.auth import Token

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# SQLModel

from sqlmodel import Session, select
from models.auth import User
from schemas.auth import UserDataForJWT

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

# I definitely need optimise this shitty func
def user_existence_verify(username: str, email: str, session: Session):
    user_username = session.exec(select(User).where(User.username == username)).first()
    user_email = session.exec(select(User).where(User.email == email)).first()
    
    if user_username and user_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"The username \'{username}\' and email \'{email}\' are already taken. Please choose another")
    if user_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"The username \'{username}\' is already taken. Please choose another")
    if user_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"The email \'{email}\' is already taken. Please choose another")
    return

def authenticate_user(username: str, password: str, session: Session)-> User:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No user with this username")
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    return dict(user)

def create_access_token(username: str, user_id: str, email: str, is_superuser: bool,
                                 expires_delta: int = settings.ACCESS_TOKEN_EXPIRES):
    to_encode = {"sub": username,
                 "user_id": user_id,
                 "email": email,
                 "is_superuser": is_superuser}
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire_time})
    token = jwt.encode(claims=to_encode, key=settings.SECRET, algorithm=settings.ALGORITHM)
    return token

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, key=settings.SECRET, algorithms=[settings.ALGORITHM])
        if payload.get("sub") is None or payload.get("user_id") is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        user_data_dict = {
            "id": payload.get("user_id"),
            "email": payload.get("email"),
            "username": payload.get("sub"),
            "is_superuser": payload.get("is_superuser")
            }
        return UserDataForJWT.model_validate(user_data_dict)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token")
    
async def get_current_superuser(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    return current_user
    
user_dependency_sqlmodel = Annotated[UserDataForJWT, Depends(get_current_user)]
