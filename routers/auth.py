from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from typing import Annotated
from database.auth import bcrypt_context, authenticate_user, create_access_token

router = APIRouter(
    prefix= '/auth',
    tags= ['auth']
)

# SQLModel
from sqlmodel import Session
from database.database import get_session
from models.auth import User, UserCreate
from database.auth import user_existence_verify
from schemas.auth import UserDataForJWT, Token

@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    user_existence_verify(username=user_data.username, email=user_data.email, session=session)
    new_user = User(
        name=user_data.name,
        surname=user_data.surname,
        username=user_data.username,
        email=user_data.email,
        hashed_password=bcrypt_context.hash(user_data.password)
    )
    session.add(new_user)
    session.commit()

@router.post('/login', status_code=status.HTTP_200_OK)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                              session: Session = Depends(get_session)) -> Token:
    user_data = authenticate_user(username=form_data.username, password=form_data.password, session=session)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    user_data = UserDataForJWT.model_validate(user_data)
    token = create_access_token(username=user_data.username, user_id=user_data.id,
                                         email=user_data.email, is_superuser=user_data.is_superuser)
    return Token(access_token=token, token_type="bearer")
