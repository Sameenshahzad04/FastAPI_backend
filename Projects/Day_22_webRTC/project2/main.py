from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database.connection import Base, engine
from routers import auth, chat
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-Time Chat App")



app.include_router(auth.r, prefix="/auth", tags=["Authentication"])
app.include_router(chat.r, prefix="/chat", tags=["Chat"])

app.mount("/static", StaticFiles(directory="static"), name="static")
# Serve HTML pages
@app.get("/")
def root():
    return FileResponse("templates/login.html")

@app.get("/login.html")
def login_page():
    return FileResponse("templates/login.html")

@app.get("/register.html")
def register_page():
    return FileResponse("templates/register.html")

@app.get("/chat.html")
def chat_page():
    return FileResponse("templates/chat.html")

