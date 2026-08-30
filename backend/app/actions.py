from sqlalchemy.orm import Session

from app.models import Account


def cancel_subscription(account_id: str, db: Session):
    account = db.query(Account).filter(
        Account.account_id == account_id
    ).first()

    if not account:
        return {
            "success": False,
            "message": "Account not found",
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


def execute_action(intent: str, account_id: str | None, db: Session):
    if intent == "cancel_subscription":
        if not account_id:
            return {
                "success": False,
                "message": "Account ID is required for cancellation",
            }

        return cancel_subscription(account_id, db)

    return {
        "success": False,
        "message": "No automated action available for this intent",
    }