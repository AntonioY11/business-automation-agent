import pytest

from app.models import Account, Approval, Customer, Refund, Request
from app.schemas import AIOperation, AIMultiRequestAnalysis, AIRequestAnalysis


def seed(db, customer_id, account_id, email):
    db.add_all([
        Customer(
            id=customer_id,
            name=f"Customer {customer_id}",
            email=email,
            subscription_status="active",
        ),
        Account(
            account_id=account_id,
            customer_id=customer_id,
            subscription_status="active",
        ),
    ])

    db.commit()


def stub_analysis(monkeypatch, **overrides):
    fields = {
        "intent": "refund_request",
        "priority": "high",
        "account_id": "ACC-1",
        "new_address": None,
        "refund_reason": "Duplicate charge",
    }
    fields.update(overrides)

    monkeypatch.setattr(
        "app.services.request_service.analyze_request",
        lambda text: AIRequestAnalysis(**fields),
    )


def test_messages_cannot_bypass_refund_approval(client, db, monkeypatch):
    seed(db, 1, "ACC-1", "bypass@example.com")

    monkeypatch.setattr(
        "app.services.conversation_service.analyze_multiple_operations",
        lambda text: AIMultiRequestAnalysis(
            operations=[
                AIOperation(
                    intent="refund_request",
                    account_id="ACC-1",
                    refund_reason="Duplicate charge",
                )
            ],
            priority="high",
        ),
    )

    response = client.post(
        "/messages",
        json={"customer_id": 1, "message": "I want a refund"},
    )

    assert response.status_code == 200

    result = response.json()["results"][0]["result"]

    assert result["status"] == "pending"
    assert db.query(Refund).count() == 0
    assert db.query(Approval).count() == 1


def test_no_approval_queued_for_someone_elses_account(client, db, monkeypatch):
    seed(db, 1, "ACC-1", "owner@example.com")
    seed(db, 2, "ACC-2", "other@example.com")

    stub_analysis(monkeypatch, account_id="ACC-2")

    response = client.post(
        "/requests",
        json={"customer_id": 1, "raw_text": "refund ACC-2"},
    )

    assert response.status_code == 200
    assert response.json()["action"]["message"] == (
        "Account does not belong to customer"
    )
    assert db.query(Approval).count() == 0
    assert db.query(Refund).count() == 0


def test_no_approval_queued_when_required_field_missing(client, db, monkeypatch):
    seed(db, 1, "ACC-1", "noreason@example.com")

    stub_analysis(monkeypatch, refund_reason=None)

    response = client.post(
        "/requests",
        json={"customer_id": 1, "raw_text": "refund me"},
    )

    assert response.json()["action"]["message"] == "Refund reason is required"
    assert db.query(Approval).count() == 0


def test_unknown_customer_is_rejected(client, db):
    response = client.post(
        "/requests",
        json={"customer_id": 9999, "raw_text": "hello"},
    )

    assert response.status_code == 404
    assert db.query(Request).count() == 0


def test_ai_failure_does_not_strand_the_request(client, db, monkeypatch):
    seed(db, 1, "ACC-1", "aifail@example.com")

    def boom(text):
        raise RuntimeError("AI service is currently unavailable.")

    monkeypatch.setattr("app.services.request_service.analyze_request", boom)

    response = client.post(
        "/requests",
        json={"customer_id": 1, "raw_text": "hello"},
    )

    assert response.status_code == 503

    db.expire_all()
    request = db.query(Request).one()

    assert request.status == "failed"
    assert request.error_message == "AI service is currently unavailable."


def test_approval_policy_has_a_single_source_of_truth():
    from app import actions
    from app.policies import requires_approval

    assert not hasattr(actions, "APPROVAL_REQUIRED_INTENTS")
    assert requires_approval("refund_request") is True
    assert requires_approval("address_change") is False


def test_malformed_ai_response_is_a_runtime_error(monkeypatch):
    from app import agent

    class FakeInteraction:
        output_text = '{"intent": "not_a_real_intent"}'

    monkeypatch.setattr(agent, "call_gemini", lambda **kw: FakeInteraction())

    with pytest.raises(RuntimeError, match="could not be understood"):
        agent.analyze_request("hello")


def test_empty_ai_response_is_a_runtime_error(monkeypatch):
    from app import agent

    class FakeInteraction:
        output_text = ""

    monkeypatch.setattr(agent, "call_gemini", lambda **kw: FakeInteraction())

    with pytest.raises(RuntimeError, match="empty response"):
        agent.analyze_request("hello")


def test_network_failure_is_a_runtime_error(monkeypatch):
    import httpx

    from app import agent

    def boom(**kwargs):
        raise httpx.ConnectTimeout("timed out")

    monkeypatch.setattr(agent.client.interactions, "create", boom)

    with pytest.raises(RuntimeError, match="unreachable"):
        agent.call_gemini("hi", {})


def test_rate_limit_is_a_runtime_error(monkeypatch):
    from google.genai import errors

    from app import agent

    def boom(**kwargs):
        raise errors.ClientError(429, {"error": {"message": "quota"}})

    monkeypatch.setattr(agent.client.interactions, "create", boom)

    with pytest.raises(RuntimeError, match="rate limit"):
        agent.call_gemini("hi", {})
