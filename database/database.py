import asyncpg
from .core import settings

async def connect_to_db():
    return await asyncpg.connect(settings.DATABASE_URL)
    
async def disconnect_from_db(connection):
    await connection.close()
    
