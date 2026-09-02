from app.schemas import AIRequestAnalysis
from app.models import Customer, Account


def test_create_request(client, db, monkeypatch):
    def fake_analyze_request(text):
        return AIRequestAnalysis(
            intent="cancel_subscription",
            priority="normal",
            account_id="ACC-001",
            new_address=None,
            refund_reason=None,
        )

    monkeypatch.setattr(
        "app.services.request_service.analyze_request",
        fake_analyze_request,
    )

    customer = Customer(
        name="Test Customer",
        email="test@example.com",
        subscription_status="active",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    account = Account(
        account_id="ACC-001",
        customer_id=customer.id,
        subscription_status="active",
    )

    db.add(account)
    db.commit()


    response = client.post(
        "/requests",
        json={
            "customer_id": customer.id,
            "raw_text": "Please cancel my subscription.",
        },
    )


    assert response.status_code == 200

    data = response.json()

    assert data["request"]["status"] == "completed"
    assert data["analysis"]["intent"] == "cancel_subscription"
    assert data["analysis"]["account_id"] == "ACC-001"
    assert data["action"]["success"] is True
    assert data["action"]["message"] == "Subscription cancelled successfully"

    assert data["request"]["action_result"] is not None
    assert "Subscription cancelled successfully" in data["request"]["action_result"]



def test_create_request_action_failure(client, db, monkeypatch):
    def fake_analyze_request(text):
        return AIRequestAnalysis(
            intent="cancel_subscription",
            priority="normal",
            account_id="ACC-999",
            new_address=None,
            refund_reason=None,
        )

    monkeypatch.setattr(
        "app.services.request_service.analyze_request",
        fake_analyze_request,
    )

    customer = Customer(
        name="Test Customer",
        email="test@example.com",
        subscription_status="active",
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    account = Account(
        account_id="ACC-999",
        customer_id=9999,
        subscription_status="active",
    )

    db.add(account)
    db.commit()

    response = client.post(
        "/requests",
        json={
            "customer_id": customer.id,
            "raw_text": "Please cancel my subscription.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["request"]["status"] == "failed"
    assert data["analysis"]["intent"] == "cancel_subscription"
    assert data["action"]["success"] is False

    assert data["request"]["action_result"] is not None