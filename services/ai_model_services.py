from db import get_database
from helpers import format_company_info, get_knowledge_base_string
from model.schema import chatRequest
import ollama
from datetime import datetime

# async def chat_endpoint_service(request: chatRequest):
#     company_info = (
#         await get_database()
#         .get_collection("users")
#         .find_one({"company_name": request.company_name})
#     )

#     if company_info:
#         company_info["_id"] = str(company_info["_id"])
#         shaped_company_info = {
#             "company_name": company_info["company_name"],
#             "founded": company_info["founded"],
#             "location": company_info["location"],
#         }

#     chat_config = (
#         await get_database()
#         .get_collection("chat_configs")
#         .find({"company_name": request.company_name})
#         .to_list()
#     )

#     shaped_chat_config = []
#     if chat_config:
#         for config in chat_config:
#             config["_id"] = str(config["_id"])
#             new_chat_config = {
#                 "question": config["question"],
#                 "answer": config["answer"],
#             }
#             shaped_chat_config.append(new_chat_config)

#     knowledge_base_str = get_knowledge_base_string(shaped_chat_config)
#     knowledge_about_company = format_company_info(shaped_company_info)

#     response = ollama.chat(
#         model="gemma3:1b",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "You are a concious smart chat assistant."
#                     "Always respond in short one or two short sentences"
#                     "Never include Asterisks (*) or markdown, or formatting when you respond. "
#                     "If user asks a complex question answer shortly first then, ask if they need a longer answer."
#                     f"{knowledge_about_company}\n"
#                     f"{knowledge_base_str}"
#                     "here also answer in plain text , do not use any markdown or formatting in your response."
#                 ),
#             },
#             {"role": "user", "content": request.message},
#         ],
#     )
#     return {"response": response["message"].content}
# return {"company_info": shaped_company_info, "chat_config": shaped_chat_config}


async def chat_endpoint_service(request: chatRequest, api: str):
    if not api:
        return {"error": "API key is required."}

    if not len(api) == 20 or not api.startswith("Ar"):
        return {"error": "Invalid API key"}

    subscription_collection = get_database().get_collection("subscriptions")
    users_collection = get_database().get_collection("users")
    chat_config_collection = get_database().get_collection("chat_configs")

    is_api_key_exists = await subscription_collection.find_one({"api_key": api})

    if not is_api_key_exists:
        return {"error": "Invalid API key not exists."}

    if is_api_key_exists["subscription_end_date"] < datetime.utcnow():
        return {
            "error": "Subscription has ended. Please renew to continue using the API."
        }

    # company info
    company_info = await users_collection.find_one(
        {"email": is_api_key_exists["user_email"]}
    )

    if company_info:
        company_info["_id"] = str(company_info["_id"])
        shaped_company_info = {
            "company_name": company_info["company_name"],
            "founded": company_info["founded"],
            "location": company_info["location"],
        }

    # chat config
    chat_config = await chat_config_collection.find(
        {"company_name": company_info["company_name"]}
    ).to_list(length=100)

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
