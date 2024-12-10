from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from database.database import get_session


router = APIRouter(
    prefix='/recipes',
    tags=['recipes']
)



# SQLModel
from sqlalchemy import and_
from sqlmodel import Session, select
from models.recipes import *
from database.auth import user_dependency_sqlmodel
from database.utils import format_ingredient_name
from schemas.auth import UserDataForJWT


# Remind to change endpoint's names

# Ingredients

@router.post("/create_ingredient_sqlmodel", status_code=status.HTTP_201_CREATED, response_model=IngredientPublic)
async def create_ingredient_sqlmodel(*, ingredient_data: IngredientCreate, session: Session = Depends(get_session),
                                     user: user_dependency_sqlmodel):
    
    ingredient_data.name = format_ingredient_name(ingredient_data.name)
    db_ingredient = session.exec(select(Ingredient).where(Ingredient.name == ingredient_data.name)).first()
    print(db_ingredient)
    if db_ingredient:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ingredient already exists")
    
    new_ingredient = Ingredient.model_validate(ingredient_data)
    session.add(new_ingredient)
    session.commit()
    session.refresh(new_ingredient)
    return new_ingredient

@router.get("/read_ingredient_by_name/{ingredient_name}", status_code=status.HTTP_200_OK, response_model=IngredientPublic)
async def read_ingredient_by_name(ingredient_name: str, session: Session = Depends(get_session)):
    ingredient_name = format_ingredient_name(ingredient_name)
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

@router.delete("/delete_ingredient_sqlmodel/{ingredient_name}", status_code=status.HTTP_200_OK)
async def delete_ingredient_sqlmodel(*, ingredient_name: str, session: Session = Depends(get_session),
                                     user: user_dependency_sqlmodel):
    ingredient_name = format_ingredient_name(ingredient_name)
    db_ingredient = session.exec(select(Ingredient).where(Ingredient.name == ingredient_name)).first()
    if not db_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    print(type(user.is_superuser))
    if user.is_superuser:
        session.delete(db_ingredient)
        session.commit()
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This user is not authorized")
    
@router.delete("/delete_ingredient_by_id/{ingredient_id}", status_code=status.HTTP_200_OK)
async def delete_ingredient_by_id(*, ingredient_id: int, session: Session = Depends(get_session),
                                  user: user_dependency_sqlmodel):
    db_ingredient = session.get(Ingredient, ingredient_id)
    if not db_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    if user.is_superuser == True:
        session.delete(db_ingredient)
        session.commit()
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This user is not authorized")

# Recipes

@router.post("/create_recipe_sqlmodel", status_code=status.HTTP_201_CREATED, response_model=RecipePublic)
async def create_recipe_sqlmodel(*, recipe_data: RecipeCreate, session: Session = Depends(get_session),
                                 user: user_dependency_sqlmodel):
    new_recipe = Recipe(
        name= recipe_data.name,
        difficulty= recipe_data.difficulty,
        recipe_type= recipe_data.recipe_type,
        steps= recipe_data.steps,
        duration= recipe_data.duration,
        owner_id= user.id
    )
    recipe_ingredients = []
    for ingredient in recipe_data.ingredients:
        ingredient.name = format_ingredient_name(ingredient.name)
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
async def read_recipe_by_ingredients(ingredient_list: list[IngredientBase],
                                     session: Session = Depends(get_session)):
    # Busqueda de ingredientes en DB
    ingredient_names = [format_ingredient_name(ingredient.name) for ingredient in ingredient_list]

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

@router.delete("/delete_recipe_by_name/{recipe_name}", status_code=status.HTTP_200_OK)
async def delete_recipe_by_name(*, recipe_name: str, session: Session = Depends(get_session),
                                user: user_dependency_sqlmodel):
    db_recipe = session.exec(select(Recipe).where(Recipe.name == recipe_name)).first()
    if not db_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if user.id == db_recipe.owner_id or user.is_superuser == True:
        session.delete(db_recipe)
        session.commit()
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This user is not authorized")
    
@router.delete("/delete_recipe_by_id/{recipe_id}", status_code=status.HTTP_200_OK)
async def delete_recipe_by_id(*, recipe_id: int, session: Session = Depends(get_session),
                              user: user_dependency_sqlmodel):
    db_recipe = session.get(Recipe, recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if user.id == db_recipe.owner_id or user.is_superuser == True:
        session.delete(db_recipe)
        session.commit()
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This user is not authorized")
    
@router.patch("/update_recipe/{recipe_name}", status_code=status.HTTP_200_OK, response_model=RecipePublic)
async def update_recipe(*, recipe_name: str, recipe_updated: RecipeUpdate, 
                        session: Session = Depends(get_session),
                        user: user_dependency_sqlmodel):
    db_recipe = session.exec(select(Recipe).where(Recipe.name == recipe_name)).first()
    if not db_recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if user.id == db_recipe.owner_id or user.is_superuser == True:
        db_recipe.sqlmodel_update(recipe_updated.model_dump(exclude_unset=True))
        session.add(db_recipe)
        session.commit()
        session.refresh(db_recipe)
        return db_recipe
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This user is not authorized")

# Temporary

@router.get("/get_recipe_by_id_user_dep/{recipe_id}", status_code=status.HTTP_200_OK, response_model=RecipePublic)
async def get_recipe_by_id_user_dep(*, recipe_id: int, session: Session = Depends(get_session),
                                    user: user_dependency_sqlmodel):
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    if user.id == recipe.owner_id or user.is_superuser == True:
        return recipe
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This user is not authorized")