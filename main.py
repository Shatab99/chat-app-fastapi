from fastapi import FastAPI
import uvicorn
import ollama
from schema import chatRequest, userRegistrationRequest, chatModel
from contextlib import asynccontextmanager
from helpers import format_company_info, get_knowledge_base_string
from db import connect_to_mongo, close_mongo_connection, get_database

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


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

@app.post("/register")
async def register_user(request: userRegistrationRequest):
    db_instance = get_database()
    users_collection = db_instance.get_collection("users")
    result = await users_collection.insert_one(request.dict())
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}

@app.post("/chat-config")
async def chat_config(request: chatModel):
    db_instance = get_database()
    chat_collection = db_instance.get_collection("chat_configs")
    result = await chat_collection.insert_one(request.dict())
    return {"message": "Chat configuration saved successfully", "config_id": str(result.inserted_id)}
    
    
    
    
@app.post("/chat")
def chat_endpoint(request: chatRequest):

    knowledge_base_str = get_knowledge_base_string(data)
    knowledge_about_company = format_company_info(companyInfo)

    response = ollama.chat(
        model="gemma3:1b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a concious smart chat assistant."
                    "Always respond in short one or two short sentences"
                    "Never include Asterisks (*) or markdown, or formatting when you respond. "
                    "If user asks a complex question answer shortly first then, ask if they need a longer answer."
                    "If someone asks you who created you answer should be: Aryy is my creator he is a sopohomore at Luther College Decorah Iowa "
                    f"{knowledge_about_company}\n"
                    f"{knowledge_base_str}"
                ),
            },
            {"role": "user", "content": request.message},
        ],
    )
    return {"response": response["message"].content}
    return {"response": knowledge_base_str}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
