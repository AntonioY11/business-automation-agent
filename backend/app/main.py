from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine
from app.models import Account, Customer, Request
from app.schemas import AccountCreate, CustomerCreate, RequestCreate


from app.agent import analyze_request


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



def cancel_subscription(account_id: str, db: Session):
    account = db.query(Account).filter(
        Account.account_id == account_id
    ).first()

    if not account:
        return {"success": False, "message": "Account not found"}

    if account.subscription_status == "cancelled":
        return {"success": False, "message": "Subscription is already cancelled"}

    account.subscription_status = "cancelled"

    db.commit()
    db.refresh(account)

    return {
        "success": True,
        "message": "Subscription cancelled successfully",
        "account_id": account.account_id,
    }



@app.post("/accounts/{account_id}/cancel")
def cancel_account(account_id: str, db: Session = Depends(get_db)):
    return cancel_subscription(account_id, db)



@app.post("/requests")
def create_request(request: RequestCreate, db: Session = Depends(get_db)):
    new_request = Request(
        customer_id=request.customer_id,
        raw_text=request.raw_text,
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    analysis = analyze_request(request.raw_text)

    new_request.intent = analysis.intent
    new_request.priority = analysis.priority
    new_request.account_id = analysis.account_id

    db.commit()
    db.refresh(new_request)

    return new_request