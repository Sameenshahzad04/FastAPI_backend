from fastapi import FastAPI
from router import router  # Correct import

app = FastAPI()

@app.get("/")
def welcome():
    return {"message": "Welcome to Mini Project"}

app.include_router(router.router, prefix='', tags=['task'])