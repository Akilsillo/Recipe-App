from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import timedelta

class Ingredients(BaseModel):
    name: str

class IngredientList(BaseModel):
    ingredient: List[Ingredients]
    
class RecipeModel(BaseModel):
    name: str
    difficulty: str
    duration: str
    recipe_type: Optional[str] = None
    
    @field_validator('duration')
    @classmethod
    def parse_duration(cls, v):
        try:
            h, m, s =  map(int, v.split(':'))
            return timedelta(hours=h, minutes=m, seconds=s)
        except ValueError:
            raise ValueError("Invalid duration format. Use HH:MM:SS")
