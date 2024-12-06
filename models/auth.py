from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    name: str
    surname: str
    username: str = Field(index=True, unique=True)
    email: str
    
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool | None = Field(default=True)
    is_superuser: bool | None = Field(default=False)
    
class UserCreate(UserBase):
    password: str
    