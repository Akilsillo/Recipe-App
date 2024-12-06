from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from typing import Annotated
from jose import jwt, JWTError
from .core import settings

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="routers/auth/login")

async def create_new_user(user_data: dict, connection):
    hashed_password = bcrypt_context.hash(user_data['password'])
    user_data['password'] = hashed_password
    user_list = [item for item in user_data.values()]
        
    user_query = """INSERT INTO users (email, name, hashed_password)
                    VALUES ($1, $2, $3)"""
        
    await connection.execute(user_query, *user_list)
    
def authenticate_user(username: str, password: str, connection):
    user = connection.fetchrow("SELECT * FROM users WHERE username = $1", username)
    if not user:
        return False
    if not bcrypt_context.verify(password, user['hashed_password']):
        return False
    return dict(user)

def create_access_token(username: str, user_id: str, is_superuser: bool, expires_delta: timedelta = settings.ACCESS_TOKEN_EXPIRES):
    to_encode = {"sub": username, "user_id": user_id, "is_superuser": is_superuser}
    expires = datetime.now(timezone.utc) + expires_delta
    to_encode.update({'exp': expires})
    token = jwt.encode(claims=to_encode, key=settings.SECRET, algorithm=settings.ALGORITHM)
    return token

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        is_superuser: bool = payload.get("is_superuser")
        return {'username': username, 'user_id': user_id, 'is_superuser': is_superuser}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
        
user_dependency = Annotated[dict ,Depends(get_current_user)]

# SQLModel

from sqlmodel import Session, select
from models.auth import User, UserBase, UserCreate
from schemas.auth import UserDataForJWT

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="routers/auth/login_sqlmodel")

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

# Change the name
def authenticate_user_sqlmodel(username: str, password: str, session: Session)-> User:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No user with this username")
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    return user

# Change the name
def create_access_token_sqlmodel(username: str, user_id: str, email: str, is_superuser: bool,
                                 expires_delta: timedelta = settings.ACCESS_TOKEN_EXPIRES):
    to_encode = {"sub": username,
                 "user_id": user_id,
                 "email": email,
                 "is_superuser": is_superuser}
    expire_time = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire_time})
    token = jwt.encode(claims=to_encode, key=settings.SECRET, algorithm=settings.ALGORITHM)
    return token

# Change the name
async def get_current_user_sqlmodel(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, key=settings.SECRET, algorithms=[settings.ALGORITHM])
        if payload.get("sub") is None or payload.get("user_id") is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {"username": payload.get("sub"),
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "is_superuser": payload.get("is_superuser")
                }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token")
    
user_dependency_sqlmodel = Annotated[dict, Depends(get_current_user_sqlmodel)]
