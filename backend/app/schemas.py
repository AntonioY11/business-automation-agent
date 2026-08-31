from pydantic import BaseModel
from typing import Literal
from datetime import datetime


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


class AIOperation(BaseModel):
    intent: Literal[
        "refund_request",
        "cancel_subscription",
        "address_change",
        "account_question",
        "create_support_ticket",
    ]

    account_id: str | None = None
    new_address: str | None = None
    refund_reason: str | None = None


class AIMultiRequestAnalysis(BaseModel):
    operations: list[AIOperation]
    priority: Literal["low", "normal", "high"]


class MessageCreate(BaseModel):
    customer_id: int
    message: str


class AuditLogResponse(BaseModel):
    id: int
    customer_id: int
    action: str
    intent: str | None
    account_id: str | None
    result: str
    details: str | None
    created_at: datetime