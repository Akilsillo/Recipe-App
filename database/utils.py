import re

def normalize_ingredients(ingredient: str)-> str:
    # 
    ingredient = re.sub(r'[áéíóúÁÉÍÓÚ ]',
                        lambda m: {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
                              'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', " ": ""}[m.group()],
                        ingredient.lower().strip())
    return ingredient