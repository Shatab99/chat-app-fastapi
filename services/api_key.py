from db import get_database
from datetime import datetime, timedelta

# 20 characters unique API key generator
import random
import string

async def create_api_key_service(email: str):
    db_instance = get_database()
    subs_collection = db_instance.get_collection("subscriptions")
    users_collection = db_instance.get_collection("users")
    user = await users_collection.find_one({"email": email})
    
    # step 1 : check if user is subscribed
    if not user:
        return {"message": "User not found"}
    if not user["isSubscribed"]:
        return {"message": "User is not subscribed"}
    
    # step 2 : does mail exist in subscriptions collection
    existing_subscription = await subs_collection.find_one({"user_email": email})
    
    if not existing_subscription:
        return {"message": "Subscription record not found"}
    
    # step 3 : check if subscription is ended or not
    if existing_subscription.get("subscription_end_date") < datetime.utcnow():
        return {"message": "Subscription has ended. Please renew to get a new API key."}
    
    # step 4 : generate unique api key and save it to subscriptions collection
    new_api_key ="".join(random.choices(string.ascii_letters + string.digits, k=20))
    if_api_key_exist = await subs_collection.find_one({"api_key": new_api_key})
    if if_api_key_exist:
        return {"message": "API key generation failed, try again"}
    result = await subs_collection.update_one({
        "user_email": email
    }, {
        "$set": {
            "api_key": new_api_key
        }
    })
    return {
        "message": "API key created successfully",
        "api_key": new_api_key,
    }