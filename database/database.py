import asyncpg
from .core import settings

async def connect_to_db():
    return await asyncpg.connect(settings.DATABASE_URL)
    
async def disconnect_from_db(connection):
    await connection.close()
    
#SQLModel
from sqlmodel import SQLModel, create_engine, Session, text
from models.recipes import Recipe, Ingredient
from models.auth import User

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
        
# Development utils        
from datetime import timedelta
from .utils import normalize_ingredients

def insert_test_data():
    with Session(engine) as session:
        cebolla = Ingredient(name=normalize_ingredients("CeBóLlÁ"))
        pimiento = Ingredient(name="pimiento")
        tomate = Ingredient(name="tomate")
        zanahoria = Ingredient(name="zanahoria")
        apio = Ingredient(name="apio")
        ajo = Ingredient(name="ajo")
        huevo = Ingredient(name="huevo")
        carne_molida = Ingredient(name=normalize_ingredients("carne molida"))
        pollo = Ingredient(name="pollo")
        salmon = Ingredient(name="salmon")
        
        session.add_all([cebolla, pimiento, tomate, zanahoria, apio, ajo, huevo, carne_molida, pollo, salmon])

        cebolla = session.get(Ingredient, 1)
        pimiento = session.get(Ingredient, 2)
        tomate = session.get(Ingredient, 3)
        zanahoria = session.get(Ingredient, 4)
        apio = session.get(Ingredient, 5)
        ajo = session.get(Ingredient, 6)
        huevo = session.get(Ingredient, 7)
        carne_molida = session.get(Ingredient, 8)
        pollo = session.get(Ingredient, 9)
        salmon = session.get(Ingredient, 10)
 
        recipe_list = [
            Recipe(name="Recipe 1", difficulty="easy", recipe_type="vegan", duration=timedelta(minutes=20),
                   ingredients=[cebolla, apio, ajo], steps="Pasos para la receta uno"),
            Recipe(name="Recipe 2", difficulty="medium", recipe_type="vegan", duration=timedelta(minutes=30),
                   ingredients=[cebolla, zanahoria, apio, ajo]),
            Recipe(name="Recipe 3", difficulty="medium", recipe_type="vegetarian", duration=timedelta(minutes=35),
                   ingredients=[cebolla, huevo, pimiento]),
            Recipe(name="Recipe 4", difficulty="difficult", recipe_type="", duration=timedelta(minutes=45),
                   ingredients=[carne_molida, pimiento, ajo]),
            Recipe(name="Recipe 5", difficulty="medium", recipe_type="", duration=timedelta(minutes=30),
                   ingredients=[salmon, tomate, cebolla]),
            Recipe(name="Recipe 6", difficulty="medium", recipe_type="", duration=timedelta(minutes=30),
                   ingredients=[pollo, zanahoria, pimiento, ajo])
        ]
        
        session.add_all(recipe_list)
        session.commit()
        
        ingredient_names = ["puerro", "choclo", "ají", "berenjena", "poroto", "lenteja", "tofu"]
        ingredient_list = []
        for name in ingredient_names:
            ingredient = Ingredient(name=name)
            ingredient_list.append(ingredient)
            
        session.add_all(ingredient_list)
        session.commit()