from asyncpg import Connection

async def get_recipe_by_name(name: str, connection: Connection):
    query = f"""SELECT * FROM recipes WHERE name = $1"""
    return await connection.fetchrow(query, name)

async def get_recipe_by_ingredients(*args, connection: Connection):
    placeholders = ",".join([f"${i+1}" for i in range(len(args))])
    print(placeholders)
    query = f"""SELECT r.name, r.difficulty, r.duration, rs.steps
    FROM recipes r
    JOIN recipes_ingredients ri ON r.id = ri.recipe_id
    JOIN ingredients i ON ri.ingredient_id = i.id
    JOIN recipes_steps rs ON r.id = rs.recipe_id
    WHERE i.name IN ({placeholders})
    GROUP BY r.name, r.difficulty, r.duration, rs.steps
    HAVING COUNT(DISTINCT i.id) = {len(args)}"""
    recipe = await connection.fetch(query, *args)
    return recipe

async def insert_new_ingredient(ingredient: str, connection: Connection):
    insert_ingredient_query = """INSERT INTO ingredients (name) VALUES ($1)
                                     ON CONFLICT (name) DO NOTHING 
                                     RETURNING id"""
    ingredient_id = await connection.fetchval(insert_ingredient_query, ingredient)
    return ingredient_id

async def insert_new_recipe(recipe_data: list, ingredients_list: list, connection: Connection)-> None:
    async with connection.transaction():
        
        recipe_query = """INSERT INTO recipes (name, difficulty, duration, recipe_type)
                          VALUES ($1, $2, $3, $4) RETURNING id"""
        recipe_id = await connection.fetchval(recipe_query, *recipe_data)
                                     
        ingredient_ids = []
        for ingredient in ingredients_list:
            ingredient_id = insert_new_ingredient(ingredient=ingredient, connection=connection)
            if ingredient_id is None:
                ingredient_id = await connection.fetchval("SELECT id FROM ingredients WHERE name = $1", ingredient)
            ingredient_ids.append(ingredient_id)
            
        recipe_ingredient_pairs = [(recipe_id, ingredient_id) for ingredient_id in ingredient_ids]
        
        recipe_ingredient_query = """INSERT INTO recipes_ingredients (recipe_id, ingredient_id)
                                     VALUES ($1, $2)"""
        await connection.executemany(recipe_ingredient_query, recipe_ingredient_pairs)