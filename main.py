from fastapi import FastAPI
from routers import recipes, auth


app = FastAPI()

@app.get("/health")
async def health_check():
    return {'status': 'Healthy'}

app.include_router(recipes.router)
app.include_router(auth.router)