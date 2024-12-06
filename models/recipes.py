from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from datetime import timedelta
from database.utils import normalize_ingredients

class RecipeIngredientLink(SQLModel, table=True):
    recipe_id: int | None = Field(default=None, foreign_key="recipe.id", primary_key=True)
    ingredient_id: int | None = Field(default=None, foreign_key="ingredient.id", primary_key=True)

# Recipes

class RecipeBase(SQLModel):
    name: str = Field(index=True)
    difficulty: str
    recipe_type: str | None
    steps: str | None = Field(max_length=200)
    # duration: str | None
    
    # @field_validator('duration')
    # @classmethod
    # def parse_duration(cls, v: str):
    #     try:
    #         h, m, s =  map(int, v.split(':'))
    #         return timedelta(hours=h, minutes=m, seconds=s)
    #     except ValueError:
    #         raise ValueError("Invalid duration format. Use HH:MM:SS")

class Recipe(RecipeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    duration: timedelta
    
    ingredients: list["Ingredient"] = Relationship(back_populates="recipes", link_model=RecipeIngredientLink)
    
class RecipeCreate(RecipeBase):
    duration: str
    ingredients: list["IngredientBase"]
    
    @field_validator('duration')
    @classmethod
    def parse_duration(cls, v: str):
        try:
            h, m, s =  map(int, v.split(':'))
            return timedelta(hours=h, minutes=m, seconds=s)
        except ValueError:
            raise ValueError("Invalid duration format. Use HH:MM:SS")
   
class RecipePublic(RecipeBase):
    id: int
    
class RecipeUpdate(SQLModel):
    name: str | None = None
    difficulty: str | None = None
    recipe_type: str | None = None
    duration: str | None = None

# Ingredients

class IngredientBase(SQLModel):
    name: str = Field(index=True, unique=True)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str):
        normalize_ingredients(v)
        return v
    
class Ingredient(IngredientBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    
    recipes: list[Recipe] = Relationship(back_populates="ingredients", link_model=RecipeIngredientLink)
    
class IngredientCreate(IngredientBase):
    pass
    

class IngredientPublic(IngredientBase):
    id: int

# Steps

# class Steps(SQLModel, table=True): # Falta añadir table=True
#     recipe_id: int | None = Field(default=None, primary_key=True, foreign_key="recipe.id") # Falta añadir foreign_key = "recipe.id"
#     steps: str = Field(default=None, max_length=200) # Funcionara? IDK ¯\_(ツ)_/¯
