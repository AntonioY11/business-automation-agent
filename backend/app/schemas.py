from pydantic import BaseModel
from typing import Literal

class CustomerCreate(BaseModel):
    name: str
    email: str
    subscription_status: str


class RequestCreate(BaseModel):
    customer_id: int
    raw_text: str


class AccountCreate(BaseModel):
    account_id: str
    customer_id: int
    subscription_status: str


class AIRequestAnalysis(BaseModel):
    intent: Literal[
        "refund_request",
        "cancel_subscription",
        "address_change",
        "account_question",
        "create_support_ticket",
    ]
    priority: Literal["low", "normal", "high"]
    account_id: str | None = None
    new_address: str | None = None
    refund_reason: str | None = None


class MessageCreate(BaseModel):
    customer_id: int
    message: str