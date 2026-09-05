from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Request, Customer
from app.schemas import RequestCreate
from app.agent import analyze_request
from app.actions import (
    process_operation,
    generate_customer_message,
)

import json


def create_request(
    request: RequestCreate,
    db: Session,
):
    customer = db.query(Customer).filter(
        Customer.id == request.customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    new_request = Request(
        customer_id=request.customer_id,
        raw_text=request.raw_text,
        status="processing",
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    try:
        analysis = analyze_request(request.raw_text)
    except RuntimeError as e:
        new_request.status = "failed"
        new_request.error_message = str(e)[:1000]
        db.commit()

        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    new_request.intent = analysis.intent
    new_request.priority = analysis.priority
    new_request.account_id = analysis.account_id

    db.commit()

    action_result = process_operation(
        analysis.intent,
        analysis.account_id,
        request.customer_id,
        analysis.new_address,
        analysis.refund_reason,
        db,
        request_id=new_request.id,
    )

    new_request.action_result = json.dumps(action_result)

    customer_message = generate_customer_message(
        analysis.intent,
        action_result,
    )

    if action_result.get("status") == "pending":
        new_request.status = "pending"
    elif action_result["success"]:
        new_request.status = "completed"
    else:
        new_request.status = "failed"
        new_request.error_message = action_result["message"][:1000]

    db.commit()
    db.refresh(new_request)

    return {
        "request": new_request,
        "analysis": analysis,
        "action": action_result,
        "customer_message": customer_message,
    }


def get_requests(db: Session):
    return db.query(Request).order_by(
        Request.created_at.desc()
    ).all()


def get_request(request_id: int, db: Session):
    request = db.query(Request).filter(
        Request.id == request_id
    ).first()

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found",
        )

    return request


def get_customer_requests(
    customer_id: int,
    db: Session,
):
    return (
        db.query(Request)
        .filter(Request.customer_id == customer_id)
        .order_by(Request.created_at.desc())
        .all()
    )