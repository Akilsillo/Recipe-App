from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from ..database.database import *
from ..database.queries import *
from ..models.models_re import *
from asyncpg.exceptions import InvalidTransactionStateError


router = APIRouter(
    prefix='/recipes',
    tags=['recipes']
)

async def get_db():
    connection = await connect_to_db()
    try:
        yield connection
    finally:
        await disconnect_from_db(connection)

@router.post("/recipe_by_ingredients", status_code=status.HTTP_200_OK)
async def recipe_by_ingredients(ingredients_list: IngredientList ,conn= Depends(get_db)):
    ingredients = [ingredient.name for ingredient in ingredients_list.ingredient]
    recipe = await get_recipe_by_ingredients(*ingredients, connection=conn)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No recipes found with these ingredients.")
    return recipe

@router.post("/create_recipe", status_code=status.HTTP_201_CREATED)
async def create_recipe(recipe: RecipeModel, ingredients_list: IngredientList, conn= Depends(get_db)):
    recipe_data = [item for item in recipe.model_dump().values()]
    ingredients = [ingredient.name for ingredient in ingredients_list.ingredient]
    
    try:
        await insert_recipe(recipe_data=recipe_data, ingredients_list=ingredients, connection=conn)
    except InvalidTransactionStateError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)