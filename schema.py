from pydantic import BaseModel

class chatRequest(BaseModel):
    message: str
    
    
class userRegistrationRequest(BaseModel):
    company_name: str
    founded: str
    location: str
    
class chatModel (BaseModel):
    company_name: str
    question: str
    answer: str