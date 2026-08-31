from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine
from app.models import Account, Customer, Request, Conversation
from app.schemas import AccountCreate, CustomerCreate, RequestCreate, MessageCreate


from app.agent import analyze_request, analyze_multiple_operations


from app.actions import execute_action, generate_customer_message, execute_operations

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


    for operation in analysis.operations:

        if (
            operation.intent == "address_change"
            and operation.account_id
            and not operation.new_address
        ):
            conversation.pending_intent = "address_change"
            conversation.pending_account_id = operation.account_id
            conversation.pending_field = "new_address"

            db.commit()

            return {
                "conversation_id": conversation.id,
                "analysis": analysis,
                "action": {
                    "success": False,
                    "message": (
                        "New address is required for address change"
                    ),
                },
                "customer_message": (
                    "I'd be happy to help change your address. "
                    "What would you like your new address to be?"
                ),
            }

    results = execute_operations(
        analysis.operations,
        message.customer_id,
        db,
    )

    return {
        "conversation_id": conversation.id,
        "analysis": analysis,
        "results": results,
    }

