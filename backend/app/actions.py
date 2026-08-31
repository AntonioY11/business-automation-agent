from sqlalchemy.orm import Session

from app.models import Account, Customer, Refund
from app.authorization import verify_account_access

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



def cancel_subscription_tool(
    account_id: str | None,
    customer_id: int,
    new_address: str | None,
    refund_reason: str | None,
    db: Session,
):
    if not account_id:
        return {
            "success": False,
            "message": "Account ID is required for cancellation",
        }

    access = verify_account_access(
        account_id,
        customer_id,
        db,
    )

    if not access["authorized"]:
        return {
            "success": False,
            "message": access["message"],
        }

    return cancel_subscription(
        account_id,
        customer_id,
        db,
    )   

def change_address_tool(
    account_id: str | None,
    customer_id: int,
    new_address: str | None,
    refund_reason: str | None,
    db: Session,
):
    if not account_id:
        return {
            "success": False,
            "message": "Account ID is required for address change",
        }
    access = verify_account_access(
        account_id,
        customer_id,
        db,
    )

    if not access["authorized"]:
        return {
            "success": False,
            "message": access["message"],
        }

    if not new_address:
        return {
            "success": False,
            "message": "New address is required for address change",
        }

    return change_address(
        account_id,
        customer_id,
        new_address,
        db,
    )


def refund_request_tool(
    account_id: str | None,
    customer_id: int,
    new_address: str | None,
    refund_reason: str | None,
    db: Session,
):
    if not account_id:
        return {
            "success": False,
            "message": "Account ID is required for refund request",
        }

    access = verify_account_access(
        account_id,
        customer_id,
        db,
    )

    if not access["authorized"]:
        return {
            "success": False,
            "message": access["message"],
        }

    if not refund_reason:
        return {
            "success": False,
            "message": "Refund reason is required",
        }

    return create_refund_request(
        account_id,
        customer_id,
        refund_reason,
        db,
    )


TOOLS = {
    "cancel_subscription": cancel_subscription_tool,
    "address_change": change_address_tool,
    "refund_request": refund_request_tool,
}

def execute_action(intent: str, account_id: str | None, customer_id: int, new_address: str | None, refund_reason: str | None, db: Session):
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




def execute_operations(
    operations,
    customer_id: int,
    db: Session,
):
    results = []

    for operation in operations:
        result = execute_action(
            operation.intent,
            operation.account_id,
            customer_id,
            operation.new_address,
            operation.refund_reason,
            db,
        )

        results.append({
            "intent": operation.intent,
            "result": result,
        })

    return results

