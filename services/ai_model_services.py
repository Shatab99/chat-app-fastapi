from db import get_database
from helpers import format_company_info, get_knowledge_base_string
from model.schema import chatRequest
import ollama

async def chat_endpoint_service(request: chatRequest):
    company_info = (
        await get_database()
        .get_collection("users")
        .find_one({"company_name": request.company_name})
    )

    if company_info:
        company_info["_id"] = str(company_info["_id"])
        shaped_company_info = {
            "company_name": company_info["company_name"],
            "founded": company_info["founded"],
            "location": company_info["location"],
        }

    chat_config = (
        await get_database()
        .get_collection("chat_configs")
        .find({"company_name": request.company_name})
        .to_list()
    )

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