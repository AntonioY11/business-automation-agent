APPROVAL_REQUIRED = {
    "cancel_subscription": True,
    "refund_request": True,
    "address_change": False,
}


def requires_approval(intent: str) -> bool:
    return APPROVAL_REQUIRED.get(intent, True)