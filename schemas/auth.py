from pydantic import BaseModel, Field


class CreateUserRequestForm(BaseModel):
    email: str = Field(max_length=100)
    name: str = Field(max_length=50)
    password: str = Field(max_length=50)
    
class Token(BaseModel):
    access_token: str
    token_type: str