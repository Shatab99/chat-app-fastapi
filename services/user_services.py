from db import get_database
from model.schema import userRegistrationRequest, chatModel


async def register_user_service(request: userRegistrationRequest):
    db_instance = get_database()
    users_collection = db_instance.get_collection("users")
    result = await users_collection.insert_one(request.dict())
    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id),
    }


async def chat_config_service(chat_data: chatModel, decoded_payload: dict):
    company_name = decoded_payload["company_name"]
    db_instance = get_database()
    chat_collection = db_instance.get_collection("chat_configs")
    data = {
        "company_name": company_name,
        "question": chat_data.question,
        "answer": chat_data.answer,
    }
    result = await chat_collection.insert_one(data)
    return {
        "message": "Chat configuration saved successfully",
        "config_id": str(result.inserted_id),
    }


async def get_chat_config_service(company_name: str):
    db_instance = get_database()
    chat_collection = db_instance.get_collection("chat_configs").find(
        {"company_name": company_name}
    )
    configs = await chat_collection.to_list(length=100)
    for config in configs:
        config["_id"] = str(config["_id"])
    return {"chat_configs": configs}


async def getProfileService(decoded_payload: dict):
    user = (
        await get_database()
        .get_collection("users")
        .find_one({"email": decoded_payload["email"]})
    )
    user["_id"] = str(user["_id"])
    return {"user": user}
