from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = 'postgresql://postgres:a3l1h2o4@localhost/RecipeApp'
    SECRET: str ='abe59a58d12726b6be031f51349b0c7d02e1522c246c5cec9fac408f8f70fb45'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRES: int = 30
    
    class Config():
        env_file = '.env'
        
settings = Settings()