APPROVAL_REQUIRED = {
    "refund_request": True,
    "cancel_subscription": False,
    "address_change": False,
    "account_question": False,
    "create_support_ticket": False,
}


def requires_approval(intent: str) -> bool:
    return APPROVAL_REQUIRED.get(intent, False)
