from fastapi import FastAPI
from database import engine
from model.model import Base
from router import r

app = FastAPI()




app.include_router(r.rou, prefix="/router", tags=["Tasks"])