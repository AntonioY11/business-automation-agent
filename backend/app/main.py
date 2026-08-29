from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine
from app.models import Customer
from app.schemas import CustomerCreate
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