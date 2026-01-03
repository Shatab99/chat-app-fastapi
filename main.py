from fastapi import Depends, FastAPI, Query
import uvicorn
from services.ai_model_services import chat_endpoint_service
from model.schema import (
    chatRequest,
    chatModel,
    userLoginRequest,
    userRegistrationRequest,
)
from services.user_services import (
    getProfileService,
    register_user_service,
    chat_config_service,
    get_chat_config_service,
)
from contextlib import asynccontextmanager
from db import connect_to_mongo, close_mongo_connection
from services.auth_services import login_service
from services.payment import subscribe_user_service
from services.api_key import create_api_key_service
from middleware import ContextMiddleware, verify_token


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

app.add_middleware(ContextMiddleware)


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
@verify_token()
async def get_profile(decoded_payload: dict = None):
    return await getProfileService(decoded_payload)

# subscribe user
@app.post("/subscribe-me")
@verify_token()
async def subscribe_user(decoded_payload: dict = None):
    email = decoded_payload.get("email")
    return await subscribe_user_service(email)

# Generate api key
@app.post("/add-api-key")
@verify_token()
async def add_api_key(decoded_payload: dict = None):
    email = decoded_payload.get("email")
    return await create_api_key_service(email)


# Chat Configuration
@app.get("/get-chat-config")
@verify_token()
async def get_chat_config_endpoint(decoded_payload: dict = None):
    return await get_chat_config_service(company_name=decoded_payload["company_name"])


@app.post("/chat-config")
@verify_token()
async def chat_config_endpoint(
    chat_data: chatModel, decoded_payload: dict = Depends(lambda: None)
):
    return await chat_config_service(chat_data, decoded_payload)


# User er kaj


@app.post("/chat")
async def chat_endpoint(request: chatRequest, api: str = Query(..., description="API Key provided in URL")):
    return await chat_endpoint_service(request, api)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=7008, reload=True)
