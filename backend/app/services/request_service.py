from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Request, Approval
from app.schemas import RequestCreate
from app.agent import analyze_request
from app.actions import (
    execute_action,
    generate_customer_message,
    create_audit_log,
    APPROVAL_REQUIRED_INTENTS,
)
from app.models import Request, Approval

import json

import json


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

    if analysis.intent in APPROVAL_REQUIRED_INTENTS:
        approval = Approval(
            customer_id=request.customer_id,
            intent=analysis.intent,
            request_id=new_request.id,
            account_id=analysis.account_id,
            new_address=analysis.new_address,
            refund_reason=analysis.refund_reason,
            status="pending",
        )

        db.add(approval)
        db.commit()
        db.refresh(approval)

        create_audit_log(
            customer_id=request.customer_id,
            action="approval_created",
            intent=analysis.intent,
            account_id=analysis.account_id,
            result="pending",
            details=f"Approval ID: {approval.id}",
            db=db,
        )

        action_result = {
            "success": False,
            "message": (
                "This operation requires human approval "
                "before it can be executed."
            ),
            "approval_id": approval.id,
            "status": "pending",
        }

    else:
        action_result = execute_action(
            analysis.intent,
            analysis.account_id,
            request.customer_id,
            analysis.new_address,
            analysis.refund_reason,
            db,
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