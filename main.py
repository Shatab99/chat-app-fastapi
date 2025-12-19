from fastapi import FastAPI
import uvicorn
import ollama
from schema import chatRequest, userRegistrationRequest, chatModel
from contextlib import asynccontextmanager
from helpers import format_company_info, get_knowledge_base_string
from db import connect_to_mongo, close_mongo_connection, get_database

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
async def register_user(request: userRegistrationRequest):
    db_instance = get_database()
    users_collection = db_instance.get_collection("users")
    result = await users_collection.insert_one(request.dict())
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}

#User login
@app.post("/login")
async def login_user(request: userRegistrationRequest):

# Chat Configuration
@app.post("/chat-config")
async def chat_config(request: chatModel):
    db_instance = get_database()
    chat_collection = db_instance.get_collection("chat_configs")
    result = await chat_collection.insert_one(request.dict())
    return {"message": "Chat configuration saved successfully", "config_id": str(result.inserted_id)}
    
    
    
# User er kaj
 
@app.post("/chat")
async def chat_endpoint(request: chatRequest):
    company_info = await get_database().get_collection("users").find_one({"company_name": request.company_name})
    
    if company_info:
        company_info["_id"] = str(company_info["_id"])
        shaped_company_info = {
            "company_name": company_info["company_name"],
            "founded": company_info["founded"],
            "location": company_info["location"],
        }
    
    chat_config = await get_database().get_collection("chat_configs").find({"company_name": request.company_name}).to_list()
    
    shaped_chat_config = []
    if chat_config:
        for config in chat_config:
            config["_id"] = str(config["_id"])
            new_chat_config = {
                "question": config["question"],
                "answer": config["answer"],
            }
            shaped_chat_config.append(new_chat_config)            

    
    knowledge_base_str = get_knowledge_base_string(shaped_chat_config)
    knowledge_about_company = format_company_info(shaped_company_info)

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
                    f"{knowledge_about_company}\n"
                    f"{knowledge_base_str}"
                    "here also answer in plain text , do not use any markdown or formatting in your response."
                ),
            },
            {"role": "user", "content": request.message},
        ],
    )
    return {"response": response["message"].content}
    # return {"company_info": shaped_company_info, "chat_config": shaped_chat_config}


if __name__ == "__main__":
     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)