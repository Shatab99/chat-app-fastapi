def get_knowledge_base_string(knowledge_data):
    # Convert the list of dicts to a clean string format
    context_str = "Knowledge Base (Use this information to answer):\n"
    for item in knowledge_data:
        context_str += f"Topic: {item['question']}\nDetails: {item['answer']}\n---\n"
    
    # Add instruction to handle multi-part questions
    context_str += (
        "\nIMPORTANT: If the user's message asks about multiple topics (e.g. both best product AND return policy), "
        "you MUST combine the details for ALL requested topics into your answer."
    )
    return context_str

def format_company_info(company_data):
    # Convert company info dict to a clean string format
    company_info_str = "Company Information:\n"
    for key, value in company_data.items():
        company_info_str += f"{key.capitalize()}: {value}\n"
    return company_info_str