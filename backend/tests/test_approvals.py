from app.models import Approval, Customer, Account, Refund

def test_reject_approval(client, db):
    customer = Customer(
        name="Approval Customer",
        email="approval@example.com",
        subscription_status="active",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    approval = Approval(
        customer_id=customer.id,
        intent="refund_request",
        account_id="TEST-010",
        refund_reason="Charged twice",
        status="pending",
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    response = client.post(
        f"/approvals/{approval.id}/reject"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["message"] == "Approval rejected"
    assert data["approval_id"] == approval.id
    assert data["status"] == "rejected"

    db.refresh(approval)

    assert approval.status == "rejected"

def test_approve_refund(client, db):
    customer = Customer(
        name="Refund Approval Customer",
        email="refund-approval@example.com",
        subscription_status="active",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    account = Account(
        account_id="TEST-011",
        customer_id=customer.id,
        subscription_status="active",
    )

    db.add(account)
    db.commit()

    approval = Approval(
        customer_id=customer.id,
        intent="refund_request",
        account_id="TEST-011",
        refund_reason="Charged twice",
        status="pending",
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    response = client.post(
        f"/approvals/{approval.id}/approve"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["message"] == "Approval executed successfully"
    assert data["approval_id"] == approval.id

    assert data["result"]["success"] is True
    assert data["result"]["message"] == (
        "Refund request created successfully"
    )

    db.refresh(approval)

    assert approval.status == "approved"

    refund = db.query(Refund).filter(
        Refund.account_id == "TEST-011"
    ).first()

    assert refund is not None
    assert refund.customer_id == customer.id
    assert refund.reason == "Charged twice"
    assert refund.status == "pending"


def test_cannot_approve_already_approved(client, db):
    customer = Customer(
        name="Already Approved Customer",
        email="already-approved@example.com",
        subscription_status="active",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    approval = Approval(
        customer_id=customer.id,
        intent="refund_request",
        account_id="TEST-012",
        refund_reason="Duplicate charge",
        status="approved",
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    response = client.post(
        f"/approvals/{approval.id}/approve"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Approval is no longer pending"