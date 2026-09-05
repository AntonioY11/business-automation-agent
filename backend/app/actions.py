from sqlalchemy.orm import Session

from app.models import Account, Customer, Refund, Approval, AuditLog
from app.authorization import verify_account_access

from app.policies import requires_approval


def create_audit_log(
    customer_id: int,
    action: str,
    intent: str | None,
    account_id: str | None,
    result: str,
    details: str | None,
    db: Session,
):
    audit = AuditLog(
        customer_id=customer_id,
        action=action,
        intent=intent,
        account_id=account_id,
        result=result,
        details=details,
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit






def cancel_subscription(account_id: str, customer_id: int, db: Session):
    account = db.query(Account).filter(
        Account.account_id == account_id
    ).first()

    if not account:
        return {
            "success": False,
            "message": "Account not found",
        }

    if account.customer_id != customer_id:
        return {
            "success": False,
            "message": "Account does not belong to customer",
        }
    

    if account.subscription_status == "cancelled":
        return {
            "success": False,
            "message": "Subscription is already cancelled",
        }

    account.subscription_status = "cancelled"

    db.commit()
    db.refresh(account)

    return {
        "success": True,
        "message": "Subscription cancelled successfully",
        "account_id": account.account_id,
    }



def change_address(
    account_id: str,
    customer_id: int,
    new_address: str,
    db: Session,
):
    account = db.query(Account).filter(
        Account.account_id == account_id
    ).first()

    if not account:
        return {
            "success": False,
            "message": "Account not found",
        }

    if account.customer_id != customer_id:
        return {
            "success": False,
            "message": "Account does not belong to customer",
        }
    
    customer = db.query(Customer).filter(
        Customer.id == account.customer_id
    ).first()

    if not customer:
        return {
            "success": False,
            "message": "Customer not found",
        }

    customer.address = new_address

    db.commit()
    db.refresh(customer)

    return {
        "success": True,
        "message": "Address updated successfully",
        "account_id": account.account_id,
        "new_address": customer.address,
    }



def create_refund_request(
    account_id: str,
    customer_id: int,
    reason: str,
    db: Session,
):
    account = db.query(Account).filter(
        Account.account_id == account_id
    ).first()

    if not account:
        return {
            "success": False,
            "message": "Account not found",
        }

    if account.customer_id != customer_id:
        return {
            "success": False,
            "message": "Account does not belong to customer",
        }

    refund = Refund(
        account_id=account_id,
        customer_id=customer_id,
        reason=reason,
        status="pending",
    )

    db.add(refund)
    db.commit()
    db.refresh(refund)

    return {
        "success": True,
        "message": "Refund request created successfully",
        "refund_id": refund.id,
        "status": refund.status,
    }



ACCOUNT_REQUIRED_MESSAGE = {
    "cancel_subscription": "Account ID is required for cancellation",
    "address_change": "Account ID is required for address change",
    "refund_request": "Account ID is required for refund request",
}

REQUIRED_FIELDS = {
    "cancel_subscription": (),
    "address_change": (
        ("new_address", "New address is required for address change"),
    ),
    "refund_request": (
        ("refund_reason", "Refund reason is required"),
    ),
}


def validate_action(
    intent: str,
    account_id: str | None,
    customer_id: int,
    new_address: str | None,
    refund_reason: str | None,
    db: Session,
):
    if intent not in TOOLS:
        return {
            "valid": False,
            "message": "No automated action available for this intent",
        }

    if not account_id:
        return {
            "valid": False,
            "message": ACCOUNT_REQUIRED_MESSAGE[intent],
        }

    access = verify_account_access(account_id, customer_id, db)

    if not access["authorized"]:
        return {
            "valid": False,
            "message": access["message"],
        }

    values = {
        "new_address": new_address,
        "refund_reason": refund_reason,
    }

    for field, message in REQUIRED_FIELDS[intent]:
        if not values[field]:
            return {
                "valid": False,
                "message": message,
            }

    return {"valid": True, "message": ""}


def _guard(intent: str):
    def decorator(fn):
        def tool(
            account_id: str | None,
            customer_id: int,
            new_address: str | None,
            refund_reason: str | None,
            db: Session,
        ):
            check = validate_action(
                intent,
                account_id,
                customer_id,
                new_address,
                refund_reason,
                db,
            )

            if not check["valid"]:
                return {
                    "success": False,
                    "message": check["message"],
                }

            return fn(
                account_id,
                customer_id,
                new_address,
                refund_reason,
                db,
            )

        return tool

    return decorator


@_guard("cancel_subscription")
def cancel_subscription_tool(
    account_id, customer_id, new_address, refund_reason, db,
):
    return cancel_subscription(account_id, customer_id, db)


@_guard("address_change")
def change_address_tool(
    account_id, customer_id, new_address, refund_reason, db,
):
    return change_address(account_id, customer_id, new_address, db)


@_guard("refund_request")
def refund_request_tool(
    account_id, customer_id, new_address, refund_reason, db,
):
    return create_refund_request(account_id, customer_id, refund_reason, db)


TOOLS = {
    "cancel_subscription": cancel_subscription_tool,
    "address_change": change_address_tool,
    "refund_request": refund_request_tool,
}


def execute_action(
    intent: str,
    account_id: str | None,
    customer_id: int,
    new_address: str | None,
    refund_reason: str | None,
    db: Session,
):
    tool = TOOLS.get(intent)

    if not tool:
        return {
            "success": False,
            "message": "No automated action available for this intent",
        }

    return tool(
        account_id,
        customer_id,
        new_address,
        refund_reason,
        db,
    )



def generate_customer_message(
    intent: str,
    action_result: dict,
):
    if action_result.get("status") == "pending":
        return (
            "Your refund request has been submitted "
            "and is pending review."
        )

    if action_result["success"]:
        if intent == "cancel_subscription":
            return "Your subscription has been cancelled successfully."

        if intent == "address_change":
            return "Your address has been updated successfully."

        if intent == "refund_request":
            return (
                "Your refund request has been created and is "
                "pending review."
            )

    message = action_result["message"]

    if message == "New address is required for address change":
        return (
            "I'd be happy to help change your address. "
            "What would you like your new address to be?"
        )

    if message == "Account ID is required for cancellation":
        return "Please provide your account ID so I can help cancel your subscription."

    if message == "Account ID is required for address change":
        return "Please provide your account ID so I can help change your address."

    if message == "Account ID is required for refund request":
        return "Please provide your account ID so I can help with your refund request."

    if message == "Refund reason is required":
        return "Please tell me why you are requesting a refund."

    if message == "Account does not belong to customer":
        return "I couldn't verify that account for your customer profile."

    if message == "Account not found":
        return "I couldn't find an account matching the information provided."

    return "I'm unable to complete your request automatically."



def create_approval(
    intent: str,
    account_id: str | None,
    customer_id: int,
    new_address: str | None,
    refund_reason: str | None,
    db: Session,
    request_id: int | None = None,
):
    approval = Approval(
        customer_id=customer_id,
        request_id=request_id,
        intent=intent,
        account_id=account_id,
        new_address=new_address,
        refund_reason=refund_reason,
        status="pending",
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    create_audit_log(
        customer_id=customer_id,
        action="approval_created",
        intent=intent,
        account_id=account_id,
        result="pending",
        details=f"Approval ID: {approval.id}",
        db=db,
    )

    return {
        "success": False,
        "message": (
            "This operation requires human approval "
            "before it can be executed."
        ),
        "approval_id": approval.id,
        "status": "pending",
    }


def process_operation(
    intent: str,
    account_id: str | None,
    customer_id: int,
    new_address: str | None,
    refund_reason: str | None,
    db: Session,
    request_id: int | None = None,
):
    check = validate_action(
        intent,
        account_id,
        customer_id,
        new_address,
        refund_reason,
        db,
    )

    if not check["valid"]:
        return {
            "success": False,
            "message": check["message"],
        }

    if requires_approval(intent):
        return create_approval(
            intent,
            account_id,
            customer_id,
            new_address,
            refund_reason,
            db,
            request_id,
        )

    return execute_action(
        intent,
        account_id,
        customer_id,
        new_address,
        refund_reason,
        db,
    )
