from app.models import Account, Customer
from app.actions import cancel_subscription, change_address, change_address_tool, create_refund_request, refund_request_tool


def test_cancel_subscription(db):
    customer = Customer(
        name="Test Customer",
        email="test@example.com",
        subscription_status="active",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    account = Account(
        account_id="TEST-001",
        customer_id=customer.id,
        subscription_status="active",
    )

    db.add(account)
    db.commit()

    result = cancel_subscription(
        account_id="TEST-001",
        customer_id=customer.id,
        db=db,
    )

    assert result["success"] is True
    assert result["message"] == "Subscription cancelled successfully"
    assert result["account_id"] == "TEST-001"

    db.refresh(account)

    assert account.subscription_status == "cancelled"



def test_cancel_subscription_wrong_customer(db):
    customer1 = Customer(
        name="Customer One",
        email="customer1@example.com",
        subscription_status="active",
    )

    customer2 = Customer(
        name="Customer Two",
        email="customer2@example.com",
        subscription_status="active",
    )

    db.add_all([customer1, customer2])
    db.commit()
    db.refresh(customer1)
    db.refresh(customer2)

    account = Account(
        account_id="TEST-002",
        customer_id=customer1.id,
        subscription_status="active",
    )

    db.add(account)
    db.commit()

    result = cancel_subscription(
        account_id="TEST-002",
        customer_id=customer2.id,
        db=db,
    )

    assert result["success"] is False
    assert result["message"] == "Account does not belong to customer"

    db.refresh(account)

    assert account.subscription_status == "active"


def test_cancel_subscription_already_cancelled(db):
    customer = Customer(
        name="Cancelled Customer",
        email="cancelled@example.com",
        subscription_status="cancelled",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    account = Account(
        account_id="TEST-003",
        customer_id=customer.id,
        subscription_status="cancelled",
    )

    db.add(account)
    db.commit()

    result = cancel_subscription(
        account_id="TEST-003",
        customer_id=customer.id,
        db=db,
    )

    assert result["success"] is False
    assert result["message"] == "Subscription is already cancelled"


def test_change_address(db):
    customer = Customer(
        name="Address Customer",
        email="address@example.com",
        subscription_status="active",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    account = Account(
        account_id="TEST-004",
        customer_id=customer.id,
        subscription_status="active",
    )

    db.add(account)
    db.commit()

    result = change_address(
        account_id="TEST-004",
        customer_id=customer.id,
        new_address="100 Hamra Street, Beirut",
        db=db,
    )

    assert result["success"] is True
    assert result["message"] == "Address updated successfully"
    assert result["account_id"] == "TEST-004"
    assert result["new_address"] == "100 Hamra Street, Beirut"

    db.refresh(customer)

    assert customer.address == "100 Hamra Street, Beirut"


def test_change_address_wrong_customer(db):
    customer1 = Customer(
        name="Customer One",
        email="one@example.com",
        subscription_status="active",
    )

    customer2 = Customer(
        name="Customer Two",
        email="two@example.com",
        subscription_status="active",
    )

    db.add_all([customer1, customer2])
    db.commit()
    db.refresh(customer1)
    db.refresh(customer2)

    account = Account(
        account_id="TEST-005",
        customer_id=customer1.id,
        subscription_status="active",
    )

    db.add(account)
    db.commit()

    result = change_address(
        account_id="TEST-005",
        customer_id=customer2.id,
        new_address="200 Beirut Street",
        db=db,
    )

    assert result["success"] is False
    assert result["message"] == "Account does not belong to customer"

    db.refresh(customer1)

    assert customer1.address is None


def test_change_address_missing_address(db):
    customer = Customer(
        name="Missing Address Customer",
        email="missing-address@example.com",
        subscription_status="active",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    account = Account(
        account_id="TEST-006",
        customer_id=customer.id,
        subscription_status="active",
    )

    db.add(account)
    db.commit()

    result = change_address_tool(
        account_id="TEST-006",
        customer_id=customer.id,
        new_address=None,
        refund_reason=None,
        db=db,
    )

    assert result["success"] is False
    assert result["message"] == "New address is required for address change"


def test_create_refund_request(db):
    customer = Customer(
        name="Refund Customer",
        email="refund@example.com",
        subscription_status="active",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    account = Account(
        account_id="TEST-007",
        customer_id=customer.id,
        subscription_status="active",
    )

    db.add(account)
    db.commit()

    result = create_refund_request(
        account_id="TEST-007",
        customer_id=customer.id,
        reason="Charged twice",
        db=db,
    )

    assert result["success"] is True
    assert result["message"] == "Refund request created successfully"
    assert result["status"] == "pending"
    assert result["refund_id"] is not None


def test_refund_request_missing_reason(db):
    customer = Customer(
        name="Missing Reason Customer",
        email="missing-reason@example.com",
        subscription_status="active",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    account = Account(
        account_id="TEST-008",
        customer_id=customer.id,
        subscription_status="active",
    )

    db.add(account)
    db.commit()

    result = refund_request_tool(
        account_id="TEST-008",
        customer_id=customer.id,
        new_address=None,
        refund_reason=None,
        db=db,
    )

    assert result["success"] is False
    assert result["message"] == "Refund reason is required"


def test_create_refund_request_wrong_customer(db):
    customer1 = Customer(
        name="Refund Owner",
        email="owner@example.com",
        subscription_status="active",
    )

    customer2 = Customer(
        name="Other Customer",
        email="other@example.com",
        subscription_status="active",
    )

    db.add_all([customer1, customer2])
    db.commit()
    db.refresh(customer1)
    db.refresh(customer2)

    account = Account(
        account_id="TEST-009",
        customer_id=customer1.id,
        subscription_status="active",
    )

    db.add(account)
    db.commit()

    result = create_refund_request(
        account_id="TEST-009",
        customer_id=customer2.id,
        reason="Charged twice",
        db=db,
    )

    assert result["success"] is False
    assert result["message"] == "Account does not belong to customer"