from pydantic import BaseModel


class chatRequest(BaseModel):
    company_name: str
    message: str


class userRegistrationRequest(BaseModel):
    company_name: str
    founded: str
    location: str
    email: str
    password: str
    
class userLoginRequest(BaseModel):
    email: str
    password: str


class chatModel(BaseModel):
    company_name: str
    question: str
    answer: str
