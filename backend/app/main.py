from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine
from app.models import Customer, Request
from app.schemas import CustomerCreate, RequestCreate


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

    db.commit()
    db.refresh(new_request)

    return new_request