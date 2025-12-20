from model.schema import userLoginRequest
from db import get_database
from helpers import  create_access_token as create_unique_token,verify_access_token

async def login_service(request: userLoginRequest):
    email = request.email
    password = request.password
    db = get_database()
    user = await db.get_collection("users").find_one({"email":email})
    if user and user["password"] == password:
        uniqueToken =create_unique_token({"email": email, "company_name": user["company_name"]})
        return {"message": "Login successful", "unique_token": uniqueToken}
    else:
        return {"message": "Invalid email or password"}
    
async def verify_token_service(token: str):
    user = verify_access_token(token)
    return user