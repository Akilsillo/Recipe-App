from fastapi import FastAPI
from .database import *
from .routers import recipes

app = FastAPI()

app.include_router(recipes.router)