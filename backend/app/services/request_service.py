from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Request
from app.schemas import RequestCreate
from app.agent import analyze_request
from app.actions import execute_action, generate_customer_message


def create_request(
    request: RequestCreate,
    db: Session,
):
    new_request = Request(
        customer_id=request.customer_id,
        raw_text=request.raw_text,
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    new_request.status = "processing"
    db.commit()

    try:
        analysis = analyze_request(request.raw_text)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    new_request.intent = analysis.intent
    new_request.priority = analysis.priority
    new_request.account_id = analysis.account_id

    db.commit()

    action_result = execute_action(
        analysis.intent,
        analysis.account_id,
        request.customer_id,
        analysis.new_address,
        analysis.refund_reason,
        db,
    )

    customer_message = generate_customer_message(
        analysis.intent,
        action_result,
    )

    if action_result["success"]:
        new_request.status = "completed"
    else:
        new_request.status = "failed"

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