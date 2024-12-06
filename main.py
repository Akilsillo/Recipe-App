from fastapi import FastAPI
from routers import recipes, auth
from database.database import create_db_and_tables, insert_test_data

import os

app = FastAPI()

# Must be changed to Lifespan when SQLModel supports async
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    insert_test_data()


@app.get("/health")
async def health_check():
    return {'status': 'Healthy'}

app.include_router(recipes.router)
app.include_router(auth.router)