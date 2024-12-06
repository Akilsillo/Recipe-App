from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from database.database import *
from database.recipes import *
from database.auth import user_dependency
from schemas.recipes import *
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
        
@router.post("/recipe_by_name", status_code=status.HTTP_200_OK)
async def recipe_by_name(recipe_name: RecipeName, conn=Depends(get_db)):
    recipe = await get_recipe_by_name(name=recipe_name.name, connection=conn)
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No recipes found with this name")
    return recipe

@router.post("/recipe_by_ingredients", status_code=status.HTTP_200_OK)
async def recipe_by_ingredients(ingredients_list: IngredientList ,conn= Depends(get_db)):
    ingredients = [ingredient.name for ingredient in ingredients_list.ingredient]
    recipe = await get_recipe_by_ingredients(*ingredients, connection=conn)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No recipes found with these ingredients.")
    return recipe

@router.post("/create_recipe", status_code=status.HTTP_201_CREATED)
async def create_recipe(recipe: RecipeModel, ingredients_list: IngredientList,
                        user: user_dependency, conn= Depends(get_db)):
    recipe_data = [item for item in recipe.model_dump().values()]
    ingredients = [ingredient.name for ingredient in ingredients_list.ingredient]
    
    try:
        await insert_new_recipe(recipe_data=recipe_data, ingredients_list=ingredients, connection=conn)
    except InvalidTransactionStateError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    

# SQLModel
from sqlalchemy import and_
from sqlmodel import Session, select
from models.recipes import *
from database.auth import user_dependency_sqlmodel

# Remind to change endpoint's names

# Ingredients

@router.post("/create_ingredient_sqlmodel", status_code=status.HTTP_201_CREATED, response_model=IngredientPublic)
async def create_ingredient_sqlmodel(ingredient_data: IngredientCreate, session: Session = Depends(get_session)):
    ingredient_data.name = normalize_ingredients(ingredient_data.name)
    new_ingredient = Ingredient.model_validate(ingredient_data)
    session.add(new_ingredient)
    session.commit()
    session.refresh(new_ingredient)
    return new_ingredient

@router.get("/read_ingredient_by_name/{ingredient_name}", status_code=status.HTTP_200_OK, response_model=IngredientPublic)
async def read_ingredient_by_name(ingredient_name: str, session: Session = Depends(get_session)):
    ingredient_name = normalize_ingredients(ingredient_name)
    db_ingredient = session.exec(select(Ingredient).where(Ingredient.name == ingredient_name)).first()
    if not db_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    return db_ingredient

@router.get("/read_ingredient_by_id/{ingredient_id}", status_code=status.HTTP_200_OK, response_model=IngredientPublic)
async def read_ingredient_by_id(ingredient_id: int, session: Session = Depends(get_session)):
    db_ingredient = session.get(Ingredient, ingredient_id)
    if not db_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    return db_ingredient

@router.delete("/delete_ingredient_sqlmodel", status_code=status.HTTP_200_OK)
async def delete_ingredient_sqlmodel(ingredient_name: IngredientBase, session: Session = Depends(get_session)):
    ingredient_name = normalize_ingredients(ingredient_name.name)
    db_ingredient = session.exec(select(Ingredient).where(Ingredient.name == ingredient_name.name)).first()
    if not db_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    session.delete(db_ingredient)
    session.commit()
    
@router.delete("/delete_ingredient_by_id/{ingredient_id}", status_code=status.HTTP_200_OK)
async def delete_ingredient_by_id(ingredient_id: int, session: Session = Depends(get_session)):
    db_ingredient = session.get(Ingredient, ingredient_id)
    if not db_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    session.delete(db_ingredient)
    session.commit()

# Recipes

@router.post("/create_recipe_sqlmodel", status_code=status.HTTP_201_CREATED, response_model=RecipePublic)
async def create_recipe_sqlmodel(recipe_data: RecipeCreate, session: Session = Depends(get_session)):
    new_recipe = Recipe(
        name= recipe_data.name,
        difficulty= recipe_data.difficulty,
        recipe_type= recipe_data.recipe_type,
        steps= recipe_data.steps,
        duration= recipe_data.duration
    )
    recipe_ingredients = []
    for ingredient in recipe_data.ingredients:
        ingredient.name = normalize_ingredients(ingredient.name)
        db_ingredient = session.exec(select(Ingredient).where(Ingredient.name == ingredient.name)).first()
        if db_ingredient is None:
            db_ingredient = Ingredient(name=ingredient.name)
        recipe_ingredients.append(db_ingredient)
    new_recipe.ingredients = recipe_ingredients
    
    
    session.add(new_recipe)
    session.commit()
    session.refresh(new_recipe)
    return new_recipe

@router.get("/read_recipe_by_name/{recipe_name}", status_code=status.HTTP_200_OK, response_model=RecipePublic)
async def read_recipe_by_name(recipe_name: str, session: Session = Depends(get_session)):
    db_recipe = session.exec(select(Recipe).where(Recipe.name == recipe_name)).first()
    if not db_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return db_recipe

@router.get("/read_recipe_by_id/{recipe_id}", status_code=status.HTTP_200_OK, response_model=RecipePublic)
async def read_recipe_by_id(recipe_id: int, session: Session = Depends(get_session)):
    db_recipe = session.get(Recipe, recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return db_recipe

# ***
@router.post("/get_recipe_by_ingredients", status_code=status.HTTP_200_OK, response_model=list[RecipePublic])
async def read_recipe_by_ingredients(ingredient_list: list[IngredientBase], session: Session = Depends(get_session)):
    # Busqueda de ingredientes en DB
    ingredient_names = [normalize_ingredients(ingredient.name) for ingredient in ingredient_list]

    db_ingredients = session.exec(select(Ingredient).where(Ingredient.name.in_(ingredient_names))).all()
        
    if len(db_ingredients) != len(ingredient_list):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Some ingredients not found")
    
    # Busqueda de receta en DB en base a los ingredientes
    db_recipe = session.exec(select(Recipe).where(
        and_(*[Recipe.ingredients.contains(ingredient) for ingredient in db_ingredients]))
        ).all()
    if not db_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No recipes found whit these ingredients")
    return db_recipe

@router.delete("/delete_recipe_by_name", status_code=status.HTTP_200_OK)
async def delete_recipe_by_name(recipe_name: RecipeBase, session: Session = Depends(get_session)):
    db_recipe = session.exec(select(Recipe).where(Recipe.name == recipe_name.name)).first()
    if not db_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    session.delete(db_recipe)
    session.commit()
    
@router.delete("/delete_recipe_by_id/{recipe_id}", status_code=status.HTTP_200_OK)
async def delete_recipe_by_id(recipe_id: int, session: Session = Depends(get_session)):
    db_recipe = session.get(Recipe, recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    session.delete(db_recipe)
    session.commit()
    
@router.patch("/update_recipe/{recipe_name}", status_code=status.HTTP_200_OK, response_model=RecipePublic)
async def update_recipe(recipe_name: str, recipe_updated: RecipeUpdate, session: Session = Depends(get_session)):
    db_recipe = session.exec(select(Recipe).where(Recipe.name == recipe_name)).first()
    if not db_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    
    db_recipe.sqlmodel_update(recipe_updated.model_dump(exclude_unset=True))
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe

# Temporary

@router.get("/get_recipe_by_id_user_dep/{recipe_id}", status_code=status.HTTP_200_OK, response_model=RecipePublic)
async def get_recipe_by_id_user_dep(*recipe_id: int, session: Session = Depends(get_session), user: user_dependency_sqlmodel):
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe