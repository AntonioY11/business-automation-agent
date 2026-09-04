from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine
from app.models import Account, Customer, Request, Conversation, Approval, AuditLog
from app.schemas import AccountCreate, CustomerCreate, RequestCreate, MessageCreate, AuditLogResponse




from app.actions import execute_action, create_audit_log


from app.services import request_service, conversation_service, customer_service

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    with Session(engine) as session:
        yield session

@app.get("/")
def root():
    return {"message": "Business Automation Agent API"}


@app.post("/customers")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    new_customer = Customer(
        name=customer.name,
        email=customer.email,
        subscription_status=customer.subscription_status,
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return new_customer


@app.get("/customers")
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return customers


@app.get("/customers/{customer_id}")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    return customer_service.get_customer(
        customer_id,
        db,
    )


@app.get("/customers/{customer_id}/requests")
def get_customer_requests(
    customer_id: int,
    db: Session = Depends(get_db),
):
    return request_service.get_customer_requests(
        customer_id,
        db,
    )


@app.post("/accounts")
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    new_account = Account(
        account_id=account.account_id,
        customer_id=account.customer_id,
        subscription_status=account.subscription_status,
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account


@app.get("/accounts/{account_id}")
def get_account(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(
        Account.account_id == account_id
    ).first()

    if not account:
        return {"error": "Account not found"}

    return account


@app.get("/approvals")
def get_pending_approvals(
    db: Session = Depends(get_db),
):
    approvals = db.query(Approval).filter(
        Approval.status == "pending"
    ).all()

    return approvals


@app.post("/approvals/{approval_id}/approve")
def approve_approval(
    approval_id: int,
    db: Session = Depends(get_db),
):
    approval = db.query(Approval).filter(
        Approval.id == approval_id
    ).first()

    if not approval:
        return {
            "success": False,
            "message": "Approval not found",
        }

    if approval.status != "pending":
        return {
            "success": False,
            "message": "Approval is no longer pending",
        }

    result = execute_action(
        approval.intent,
        approval.account_id,
        approval.customer_id,
        approval.new_address,
        approval.refund_reason,
        db,
    )

    if not result["success"]:
        create_audit_log(
            customer_id=approval.customer_id,
            action="approval_execution_failed",
            intent=approval.intent,
            account_id=approval.account_id,
            result="failed",
            details=result["message"],
            db=db,
        )

        return {
            "success": False,
            "message": "Operation failed",
            "approval_id": approval.id,
            "result": result,
        }

    approval.status = "approved"

    request = db.query(Request).filter(
    Request.id == approval.request_id
    ).first()

    if request:
        request.status = "completed"

    db.commit()
    db.refresh(approval)

    create_audit_log(
        customer_id=approval.customer_id,
        action="approval_approved",
        intent=approval.intent,
        account_id=approval.account_id,
        result="success",
        details=f"Approval ID: {approval.id}",
        db=db,
    )

    return {
        "success": True,
        "message": "Approval executed successfully",
        "approval_id": approval.id,
        "result": result,
    }



@app.post("/approvals/{approval_id}/reject")
def reject_approval(
    approval_id: int,
    db: Session = Depends(get_db),
):
    approval = db.query(Approval).filter(
        Approval.id == approval_id
    ).first()

    if not approval:
        return {
            "success": False,
            "message": "Approval not found",
        }

    if approval.status != "pending":
        return {
            "success": False,
            "message": "Approval is no longer pending",
        }

    approval.status = "rejected"

    request = db.query(Request).filter(
        Request.id == approval.request_id
    ).first()

    if request:
        request.status = "rejected"

    db.commit()
    db.refresh(approval)

    create_audit_log(
        customer_id=approval.customer_id,
        action="approval_rejected",
        intent=approval.intent,
        account_id=approval.account_id,
        result="rejected",
        details=f"Approval ID: {approval.id}",
        db=db,
    )

    return {
        "success": True,
        "message": "Approval rejected",
        "approval_id": approval.id,
        "status": approval.status,
    }




@app.post("/requests")
def create_request(request: RequestCreate, db: Session = Depends(get_db)):
    return request_service.create_request(
        request,
        db,
    )



@app.get("/requests")
def get_requests(
    db: Session = Depends(get_db),
):
    return request_service.get_requests(db)


@app.get("/requests/{request_id}")
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
):
    return request_service.get_request(
        request_id,
        db,
    )


@app.post("/messages")
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
):
    return conversation_service.create_message(
        message,
        db,
    )


@app.get("/audit-logs", response_model=list[AuditLogResponse])
def get_audit_logs(
    customer_id: int | None = None,
    intent: str | None = None,
    action: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)

    if customer_id is not None:
        query = query.filter(
            AuditLog.customer_id == customer_id
        )

    if intent is not None:
        query = query.filter(
            AuditLog.intent == intent
        )

    if action is not None:
        query = query.filter(
            AuditLog.action == action
        )

    return (
        query
        .order_by(AuditLog.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )