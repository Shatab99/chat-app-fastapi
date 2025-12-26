from model.schema import userRegistrationRequest
from db import get_database
from bson import ObjectId
from datetime import datetime, timedelta


async def subscribe_user_service(email: str):
    # payment processing logic would go here (e.g., interacting with a payment gateway)
    db_instance = get_database()
    users_collection = db_instance.get_collection("users")
    user_subscription = db_instance.get_collection("subscriptions")
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
