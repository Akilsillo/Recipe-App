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