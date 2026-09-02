from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Customer


def get_customer(customer_id: int, db: Session):
    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer