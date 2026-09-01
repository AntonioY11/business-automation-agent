from app.schemas import AIMultiRequestAnalysis, AIOperation
from app.models import Customer, Account


def test_create_message_cancel_subscription(client, db, monkeypatch):
    def fake_analyze_multiple_operations(text):
        return AIMultiRequestAnalysis(
            operations=[
                AIOperation(
                    intent="cancel_subscription",
                    account_id="ACC-001",
                    new_address=None,
                    refund_reason=None,
                )
            ],
            priority="normal",
        )

    monkeypatch.setattr(
        "app.services.conversation_service.analyze_multiple_operations",
        fake_analyze_multiple_operations,
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
        "/messages",
        json={
            "customer_id": customer.id,
            "message": "Please cancel my subscription.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["analysis"]["operations"][0]["intent"] == (
        "cancel_subscription"
    )

    assert data["results"][0]["result"]["success"] is True

    assert data["results"][0]["result"]["message"] == (
        "Subscription cancelled successfully"
    )




def test_create_message_address_change_missing_address(
    client,
    db,
    monkeypatch,
):
    def fake_analyze_multiple_operations(text):
        return AIMultiRequestAnalysis(
            operations=[
                AIOperation(
                    intent="address_change",
                    account_id="ACC-001",
                    new_address=None,
                    refund_reason=None,
                )
            ],
            priority="normal",
        )

    monkeypatch.setattr(
        "app.services.conversation_service.analyze_multiple_operations",
        fake_analyze_multiple_operations,
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
        "/messages",
        json={
            "customer_id": customer.id,
            "message": "I want to change my address.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["pending_operation"]["intent"] == "address_change"
    assert data["pending_operation"]["account_id"] == "ACC-001"

    assert data["customer_message"] == (
        "I'd be happy to help change your address. "
        "What would you like your new address to be?"
    )



def test_create_message_address_change_follow_up(
    client,
    db,
    monkeypatch,
):
    def fake_analyze_multiple_operations(text):
        if text == "I want to change my address.":
            return AIMultiRequestAnalysis(
                operations=[
                    AIOperation(
                        intent="address_change",
                        account_id="ACC-001",
                        new_address=None,
                        refund_reason=None,
                    )
                ],
                priority="normal",
            )

        return AIMultiRequestAnalysis(
            operations=[
                AIOperation(
                    intent="address_change",
                    account_id="ACC-001",
                    new_address="123 Main Street",
                    refund_reason=None,
                )
            ],
            priority="normal",
        )

    monkeypatch.setattr(
        "app.services.conversation_service.analyze_multiple_operations",
        fake_analyze_multiple_operations,
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

    first_response = client.post(
        "/messages",
        json={
            "customer_id": customer.id,
            "message": "I want to change my address.",
        },
    )

    assert first_response.status_code == 200

    first_data = first_response.json()

    assert first_data["pending_operation"]["intent"] == "address_change"

    second_response = client.post(
        "/messages",
        json={
            "customer_id": customer.id,
            "message": "123 Main Street",
        },
    )

    assert second_response.status_code == 200

    second_data = second_response.json()

    assert second_data["action"]["success"] is True

    assert second_data["customer_message"] == (
        "Your address has been updated successfully."
    )

    conversation = db.query(
        __import__("app.models", fromlist=["Conversation"]).Conversation
    ).filter(
        __import__("app.models", fromlist=["Conversation"]).Conversation.customer_id
        == customer.id
    ).first()

    assert conversation.pending_intent is None
    assert conversation.pending_account_id is None
    assert conversation.pending_field is None
