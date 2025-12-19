from fastapi import FastAPI
import uvicorn
from ai_model_services import chat_endpoint_service
from schema import chatRequest, chatModel, userLoginRequest, userRegistrationRequest
from user_services import getProfileService, register_user_service, chat_config_service
from contextlib import asynccontextmanager
from db import connect_to_mongo, close_mongo_connection
from auth_services import login_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Ollama client or any other resources if needed
    print("Starting up...")
    await connect_to_mongo()
    yield
    # Shutdown: Clean up resources if needed
    await close_mongo_connection()
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


# User Registration
@app.post("/register")
async def register_user_endpoint(request: userRegistrationRequest):
    return await register_user_service(request)


# User login
@app.post("/login")
async def login_user(request: userLoginRequest):
    return await login_service(request)

@app.get("/profile")
async def get_profile(token: str):
    return await getProfileService(token)
    


# Chat Configuration
@app.post("/chat-config")
async def chat_config_endpoint(request: chatModel):
    return await chat_config_service(request)


# User er kaj


@app.post("/chat")
async def chat_endpoint(request: chatRequest):
    return await chat_endpoint_service(request)
    


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
