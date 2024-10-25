import asyncpg
from .core import settings

async def connect_to_db():
    return await asyncpg.connect(settings.DATABASE_URL)
    
async def disconnect_from_db(connection):
    await connection.close()
    
#SQLModel
from sqlmodel import SQLModel, create_engine, Session, text
from models.recipes import *

#Development and Test DB

sqlite_url = "sqlite:///database.db"

engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread":False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))

def get_session():
    with Session(engine) as session:
        yield session
        