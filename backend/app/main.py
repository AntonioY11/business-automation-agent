from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine
from app.models import Account, Customer, Request, Conversation, Approval, AuditLog
from app.schemas import AccountCreate, CustomerCreate, RequestCreate, MessageCreate, AuditLogResponse


from app.agent import analyze_request, analyze_multiple_operations


from app.actions import execute_action, generate_customer_message, execute_operations, create_audit_log

app = FastAPI()


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
    new_request = Request(
        customer_id=request.customer_id,
        raw_text=request.raw_text,
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    new_request.status = "processing"
    db.commit()

    analysis = analyze_request(request.raw_text)

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


@app.post("/messages")
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(
        Conversation.customer_id == message.customer_id,
        Conversation.status == "active",
    ).first()

    if not conversation:
        conversation = Conversation(
            customer_id=message.customer_id,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    if conversation.pending_field == "new_address":
        analysis = analyze_multiple_operations(message.message)

        new_address = None

        for operation in analysis.operations:
            if operation.new_address:
                new_address = operation.new_address
                break

        if new_address:
            action_result = execute_action(
                "address_change",
                conversation.pending_account_id,
                message.customer_id,
                new_address,
                None,
                db,
            )

            if action_result["success"]:
                conversation.pending_intent = None
                conversation.pending_account_id = None
                conversation.pending_field = None

                db.commit()

                return {
                    "conversation_id": conversation.id,
                    "analysis": analysis,
                    "action": action_result,
                    "customer_message": (
                        "Your address has been updated successfully."
                    ),
                }

            return {
                "conversation_id": conversation.id,
                "analysis": analysis,
                "action": action_result,
            }


    analysis = analyze_multiple_operations(message.message)

    results = []
    pending_operation = None


    for operation in analysis.operations:

        if (
            operation.intent == "address_change"
            and operation.account_id
            and not operation.new_address
        ):
            pending_operation = operation
            continue


        result = execute_action(
            operation.intent,
            operation.account_id,
            message.customer_id,
            operation.new_address,
            operation.refund_reason,
            db,
        )

        results.append({
            "intent": operation.intent,
            "result": result,
        })


    if pending_operation:
        conversation.pending_intent = pending_operation.intent
        conversation.pending_account_id = pending_operation.account_id
        conversation.pending_field = "new_address"

        db.commit()

    if pending_operation:

        if results:
            successful_actions = [
                item
                for item in results
                if item["result"]["success"]
            ]

            if successful_actions:
                message_text = (
                    "I've completed the available request. "
                    "What would you like your new address to be?"
                )
            else:
                message_text = (
                    "I need your new address to complete "
                    "the address change."
                )
        else:
            message_text = (
                "I'd be happy to help change your address. "
                "What would you like your new address to be?"
            )

        return {
            "conversation_id": conversation.id,
            "analysis": analysis,
            "results": results,
            "pending_operation": {
                "intent": pending_operation.intent,
                "account_id": pending_operation.account_id,
            },
            "customer_message": message_text,
        }

    return {
        "conversation_id": conversation.id,
        "analysis": analysis,
        "results": results,
    }


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