from .core import settings

#SQLModel
from sqlmodel import SQLModel, create_engine, Session, text
from models.recipes import Recipe, Ingredient
from models.auth import User


engine = create_engine(settings.DATABASE_URL, echo=True, connect_args={"check_same_thread":False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON")) # This line is only for sqlite DB

def get_session():
    with Session(engine) as session:
        yield session
        