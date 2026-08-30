from sqlalchemy.orm import Session

from app.models import Account, Customer


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



def execute_action(intent: str, account_id: str | None, customer_id: int, new_address: str | None, db: Session):
    if intent == "cancel_subscription":
        if not account_id:
            return {
                "success": False,
                "message": "Account ID is required for cancellation",
            }

        return cancel_subscription(account_id, customer_id, db)



    if intent == "address_change":
        if not account_id:
            return {
                "success": False,
                "message": "Account ID is required for address change",
            }

        if not new_address:
            return {
                "success": False,
                "message": "New address is required for address change",
            }

        return change_address(account_id, customer_id, new_address, db)

    return {
        "success": False,
        "message": "No automated action available for this intent",
    }

    return {
        "success": False,
        "message": "No automated action available for this intent",
    }

