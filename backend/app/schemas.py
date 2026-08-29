from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str
    email: str
    subscription_status: str


class RequestCreate(BaseModel):
    customer_id: int
    raw_text: str