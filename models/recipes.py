from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from datetime import timedelta

class RecipeIngredientLink(SQLModel, table=True):
    recipe_id: int | None = Field(default=None, foreign_key="recipe.id", primary_key=True)
    ingredient_id: int | None = Field(default=None, foreign_key="ingredient.id", primary_key=True)

class RecipeBase(SQLModel):
    name: str = Field(index=True)
    difficulty: str
    recipe_type: str | None
    duration: str
    
    @field_validator('duration')
    @classmethod
    def parse_duration(cls, v):
        try:
            h, m, s =  map(int, v.split(':'))
            return timedelta(hours=h, minutes=m, seconds=s)
        except ValueError:
            raise ValueError("Invalid duration format. Use HH:MM:SS")

class Recipe(RecipeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    
    ingredients: list["Ingredient"] = Relationship(back_populates="recipes", link_model=RecipeIngredientLink)
    
class RecipeCreate(RecipeBase):
    pass
    
class RecipePublic(RecipeBase):
    id: int
    
class IngredientBase(SQLModel):
    name: str = Field(index=True)
    
class Ingredient(IngredientBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    
    recipes: list[Recipe] = Relationship(back_populates="ingredients", link_model=RecipeIngredientLink)
    
class IngredientCreate(IngredientBase):
    pass

class IngredientPublic(IngredientBase):
    id: int