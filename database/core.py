from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = 'Choose your DB url'
    SECRET: str ='Choose your secret'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRES: int = 30
    
    class Config():
        env_file = '.env'
        
settings = Settings()