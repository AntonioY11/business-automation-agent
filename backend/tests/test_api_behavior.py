import json

import pytest

from app.models import Account, Approval, Customer, Refund, Request
from app.schemas import AIRequestAnalysis


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


def test_missing_resources_return_404(client, db):
    assert client.get("/requests/999").status_code == 404
    assert client.get("/customers/999").status_code == 404
    assert client.get("/accounts/NOPE").status_code == 404
    assert client.post("/approvals/999/approve").status_code == 404
    assert client.post("/approvals/999/reject").status_code == 404


def test_duplicate_email_returns_409(client, db):
    payload = {
        "name": "Dup",
        "email": "dup@example.com",
        "subscription_status": "active",
    }

    assert client.post("/customers", json=payload).status_code == 200
    assert client.post("/customers", json=payload).status_code == 409


def test_duplicate_account_id_returns_409(client, db):
    seed(db, 1, "ACC-1", "acct@example.com")

    response = client.post(
        "/accounts",
        json={
            "account_id": "ACC-1",
            "customer_id": 1,
            "subscription_status": "active",
        },
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"customer_id": 1, "raw_text": "x" * 5001},
        {"customer_id": 1, "raw_text": ""},
    ],
)
def test_oversized_and_empty_text_are_422(client, db, payload):
    assert client.post("/requests", json=payload).status_code == 422


@pytest.mark.parametrize(
    "query",
    ["limit=-1", "limit=0", "offset=-5", "limit=100000"],
)
def test_audit_log_pagination_bounds(client, db, query):
    assert client.get(f"/audit-logs?{query}").status_code == 422


def test_approving_refreshes_request_action_result(client, db, monkeypatch):
    seed(db, 1, "ACC-1", "approve@example.com")
    stub_analysis(monkeypatch)

    client.post("/requests", json={"customer_id": 1, "raw_text": "refund"})

    approval = db.query(Approval).one()

    assert approval.request_id is not None

    client.post(f"/approvals/{approval.id}/approve")

    db.expire_all()
    request = db.query(Request).one()

    assert request.status == "completed"

    action_result = json.loads(request.action_result)

    assert action_result["success"] is True
    assert action_result["message"] == "Refund request created successfully"


def test_rejecting_marks_request_rejected(client, db, monkeypatch):
    seed(db, 1, "ACC-1", "reject@example.com")
    stub_analysis(monkeypatch)

    client.post("/requests", json={"customer_id": 1, "raw_text": "refund"})

    approval = db.query(Approval).one()
    client.post(f"/approvals/{approval.id}/reject")

    db.expire_all()
    request = db.query(Request).one()

    assert request.status == "rejected"
    assert json.loads(request.action_result)["status"] == "rejected"
    assert db.query(Refund).count() == 0


def test_approval_is_executed_only_once(client, db, monkeypatch):
    seed(db, 1, "ACC-1", "once@example.com")
    stub_analysis(monkeypatch)

    client.post("/requests", json={"customer_id": 1, "raw_text": "refund"})
    approval = db.query(Approval).one()

    assert client.post(f"/approvals/{approval.id}/approve").status_code == 200
    assert client.post(f"/approvals/{approval.id}/approve").status_code == 409
    assert db.query(Refund).count() == 1
