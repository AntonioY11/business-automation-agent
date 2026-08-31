from sqlalchemy.orm import Session

from app.models import Account


def verify_account_access(
    account_id: str,
    customer_id: int,
    db: Session,
):
    account = db.query(Account).filter(
        Account.account_id == account_id
    ).first()

    if not account:
        return {
            "authorized": False,
            "message": "Account not found",
        }

    if account.customer_id != customer_id:
        return {
            "authorized": False,
            "message": "Account does not belong to customer",
        }

    return {
        "authorized": True,
        "account": account,
    }