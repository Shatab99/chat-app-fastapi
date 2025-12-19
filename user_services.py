from db import get_database
from schema import userRegistrationRequest,chatModel
from helpers import verify_access_token


async def register_user_service(request: userRegistrationRequest):
    db_instance = get_database()
    users_collection = db_instance.get_collection("users")
    result = await users_collection.insert_one(request.dict())
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}

async def chat_config_service(request: chatModel):
    db_instance = get_database()
    chat_collection = db_instance.get_collection("chat_configs")
    result = await chat_collection.insert_one(request.dict())
    return {"message": "Chat configuration saved successfully", "config_id": str(result.inserted_id)}

async def getProfileService(token: str):
    deocode_user = verify_access_token(token)
    db_instance = get_database()
    users_collection = db_instance.get_collection("users")
    users = await users_collection.find_one({"email": deocode_user["email"]})
    if users:
        users["_id"] = str(users["_id"])
    return {"user": users}