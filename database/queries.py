

async def get_recipe_by_ingredients(*args, connection):
    placeholders = ",".join([f"%s" for _ in args])
    query = f"""SELECT r.name, r.difficulty, r.duration
    FROM recipes r
    JOIN recipes_ingredients ri ON r.id = ri.recipe_id
    JOIN ingredients i ON ri.ingredient_id = i.id
    WHERE i.name IN ({placeholders})
    GROUP BY r.name, r.difficulty, r.duration
    HAVING COUNT(DISTINCT i.id) = {len(args)}"""
    print(query)
    recipe = await connection.fetch(query, *args)
    return recipe

async def insert_recipe(recipe_data: list, ingredients_list: list, connection):
    async with connection.transaction():
        
        recipe_query = """INSERT INTO recipes (name, difficulty, duration, recipe_type)
                          VALUES ($1, $2, $3, $4) RETURNING id"""
        recipe_id = await connection.fetchval(recipe_query, *recipe_data)
        
        insert_ingredient_query = """INSERT INTO ingredients (name) VALUES ($1)
                                     ON CONFLICT (name) DO NOTHING 
                                     RETURNING id"""
                                     
        ingredient_ids = []
        for i in ingredients_list:
            ingredient_id = await connection.fetchval(insert_ingredient_query, i)
            if ingredient_id is None:
                ingredient_id = await connection.fetchval("SELECT id FROM ingredients WHERE name = $1", i)
            ingredient_ids.append(ingredient_id)
            
        recipe_ingredient_pairs = [(recipe_id, ingredient_id) for ingredient_id in ingredient_ids]
        
        recipe_ingredient_query = """INSERT INTO recipes_ingredients (recipe_id, ingredient_id)
                                     VALUES ($1, $2)"""
        await connection.executemany(recipe_ingredient_query, recipe_ingredient_pairs)