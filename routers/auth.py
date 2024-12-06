from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2, OAuth2PasswordRequestForm
from starlette import status
from typing import Annotated
from database.database import *
from database.auth import *
from schemas.auth import *

router = APIRouter(
    prefix= '/auth',
    tags= ['auth']
)

async def get_db():
    connection = await connect_to_db()
    try:
        yield connection
    finally:
        await disconnect_from_db(connection)
        

@router.post('/create_user', status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUserRequestForm, connection= Depends(get_db)):
    user_data = user.model_dump()
    await create_new_user(user_data=user_data, connection=connection)
    return {"message": "User created successfully"}

@router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                     connection= Depends(get_db)):
    user_data = await authenticate_user(form_data.username, form_data.password, connection=connection)
    if not user_data:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail='Could not validate user.')
    token = create_access_token(user_data.username, user_data.user_id, user_data.is_superuser)
    return {'access_token': token, 'token_type': 'bearer'}

# SQLModel
from sqlmodel import Session
from database.database import get_session
from models.auth import User, UserCreate
from database.auth import user_existence_verify
from schemas.auth import UserDataForJWT

@router.post('/create_user_sqlmodel', status_code=status.HTTP_201_CREATED)
async def create_user_sqlmodel(user_data: UserCreate, session: Session = Depends(get_session)):
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

@router.post('/login_sqlmodel', status_code=status.HTTP_200_OK)
async def login_user_sqlmodel(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                              session: Session = Depends(get_session)):
    user_data = authenticate_user_sqlmodel(username=form_data.username, password=form_data.password, session=session)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    user_data = UserDataForJWT.model_validate(user_data)
    token = create_access_token_sqlmodel(username=user_data.username, user_id=user_data.id,
                                         email=user_data.email, is_superuser=user_data.is_superuser)
    return {'access_token': token, 'token_type': 'bearer'}