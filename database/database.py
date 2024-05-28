import asyncpg

async def connect_to_db():
    return await asyncpg.connect('postgresql://postgres:a3l1h2o4@localhost/RecipeApp')
    
async def disconnect_from_db(connection):
    await connection.close()
    
