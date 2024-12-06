import pytest
import asyncpg
from datetime import timedelta
from fastapi.testclient import TestClient
from main import app
from schemas.auth import CreateUserRequestForm
from schemas.recipes import *
from database.recipes import insert_new_recipe

from httpx import AsyncClient, ASGITransport

transport = ASGITransport(app=app)

client = TestClient(app)

DATABASE_URL = 'postgresql://postgres:a3l1h2o4@localhost/RecipeAppTest'

async def override_get_db():
    connection = await asyncpg.connect(DATABASE_URL)
    try:
        yield connection
    finally:
        await connection.close()
        
def override_get_current_user():
    return {'username': 'Andres', 'user_id': 1, 'is_superuser': False}

@pytest.fixture
def test_user():
    user = CreateUserRequestForm

# No se está ejecutando la fixture al momento de correr los test.   
@pytest.fixture
async def test_recipe():
    ingredients = [['Spaghetti'], ['Pecorino romano'], ['Huevo'], ['Guanciale']]
    recipe_query = f"""INSERT INTO recipes (name, difficulty, duration)
                VALUES ('Spaghetti carbonara', 'easy', '{timedelta(minutes=25)}')"""
    ingredients_query = "INSERT INTO ingredients (name) VALUES ($1)"
    recipes_ingredients_query = """INSERT INTO recipes_ingredients (recipe_id, ingredient_id)
                                    VALUES ((SELECT id FROM recipes WHERE name = 'Spaghetti carbonara'), $1)"""

    # Use el método para conectarse dentro del contexto de la prueba
    pool = await asyncpg.create_pool(DATABASE_URL)

    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(recipe_query)
            await connection.executemany(ingredients_query, ingredients)
            for i in ingredients:
                ingredient_id = await connection.fetchval("SELECT id FROM ingredients WHERE name = $1", i[0])
                await connection.execute(recipes_ingredients_query, ingredient_id)
        
        yield await connection.fetch("SELECT * FROM recipes")

    # Limpiar la base de datos después de las pruebas
    async with pool.acquire() as connection:
        await connection.execute("""DELETE FROM recipes_ingredients;
                                    DELETE FROM ingredients;
                                    DELETE FROM recipes;""")
    await pool.close()
        
        
        
from fastapi import status
from routers.recipes import get_db
from database.auth import get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.mark.anyio
async def test_recipe_by_name(test_recipe):
    async with AsyncClient(transport=transport, base_url= "http://test") as client:
        response = await client.post("/recipes/recipe_by_name", json={"name": "Spaghetti carbonara"})
    assert response.status_code == status.HTTP_200_OK

    