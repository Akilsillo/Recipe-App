from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from typing import Annotated
from jose import jwt, JWTError
from core import settings

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