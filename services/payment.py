from model.schema import userRegistrationRequest
from db import get_database
from bson import ObjectId
from datetime import datetime, timedelta


async def subscribe_user_service(email: str):
    # payment processing logic would go here (e.g., interacting with a payment gateway)
    db_instance = get_database()
    users_collection = db_instance.get_collection("users")
    user_subscription = db_instance.get_collection("subscriptions")
    
    # Renew subscription for existing subscribed users
    existing_subscription = await user_subscription.find_one({"user_email": email})
    if existing_subscription:
        new_end_date = existing_subscription["subscription_end_date"] + timedelta(days=30)
        await user_subscription.update_one(
            {"user_email": email},
            {"$set": {"subscription_end_date": new_end_date}}
        )
        return {"message": "Subscription renewed successfully"}
    
    result = await users_collection.update_one(
        {"email": email}, {"$set": {"isSubscribed": True}}
    )
    if result.modified_count == 1:
        await user_subscription.insert_one(
            {
                "user_email": email,
                "subscription_end_date": datetime.utcnow() + timedelta(days=30),
            }
        )
        return {"message": "User subscribed successfully"}
    else:
        return {"message": "User not found or already subscribed"}
