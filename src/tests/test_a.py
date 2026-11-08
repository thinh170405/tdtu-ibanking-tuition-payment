import importlib
import os
from datetime import datetime, timedelta, timezone

import jwt

from fastapi.testclient import TestClient


def test_account_login_profile_and_validation(tmp_path, monkeypatch):
    monkeypatch.setenv("ACCOUNT_DATABASE_URL", "sqlite:///" + str(tmp_path / "account.db"))
    account = importlib.import_module("services.account.app")
    account.Base.metadata.create_all(account.engine)
    with account.SessionLocal.begin() as db:
        db.add(account.User(id="u1", username="demo1", password_hash=account.hasher.hash("Demo!2026"), full_name="Nguyễn Văn An", phone="0900000001", email="demo1@example.test"))
    client = TestClient(account.app)
    assert client.post("/api/v1/auth/login", json={"username": "demo1", "password": "wrong"}).status_code == 401
    invalid = client.post("/api/v1/auth/login", json={"username": "demo1", "password": "Demo!2026", "extra": 1})
    assert invalid.status_code == 400 and invalid.json()["code"] == "VALIDATION_ERROR"
    response = client.post("/api/v1/auth/login", json={"username": "demo1", "password": "Demo!2026"})
    assert response.status_code == 200
    token = response.json()["accessToken"]
    profile = client.get("/api/v1/users/me", headers={"Authorization": "Bearer " + token})
    assert profile.json() == {"userId": "u1", "fullName": "Nguyễn Văn An", "phone": "0900000001", "email": "demo1@example.test"}
    assert client.get("/api/v1/users/me").json()["code"] == "UNAUTHORIZED"


def test_notification_idempotency_conflict_and_retry(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTIFICATION_DATABASE_URL", "sqlite:///" + str(tmp_path / "notification.db"))
    monkeypatch.setenv("INTERNAL_API_KEY", "test-key")
    notification = importlib.import_module("services.notification.app")
    notification.Base.metadata.create_all(notification.engine)
    sent = []
    monkeypatch.setattr(notification, "send_email", lambda mail: sent.append(mail))
    client = TestClient(notification.app)
    body = {"messageId": "otp:p1", "type": "OTP", "to": "user@example.com", "data": {"paymentId": "p1", "otp": "123456", "expiresAt": "2026-11-03T12:05:00Z"}}
    assert client.post("/internal/v1/notifications/email", json=body).status_code == 403
    headers = {"X-Internal-Key": "test-key"}
    assert client.post("/internal/v1/notifications/email", json=body, headers=headers).json() == {"messageId": "otp:p1", "status": "SENT"}
    assert client.post("/internal/v1/notifications/email", json=body, headers=headers).status_code == 200
    assert len(sent) == 1
    changed = {**body, "data": {**body["data"], "otp": "654321"}}
    assert client.post("/internal/v1/notifications/email", json=changed, headers=headers).json()["code"] == "MESSAGE_ID_CONFLICT"
    assert len(sent) == 1
    failing = {**body, "messageId": "otp:p2", "data": {**body["data"], "paymentId": "p2"}}
    def fail_once(mail):
        raise OSError("SMTP unavailable")
    monkeypatch.setattr(notification, "send_email", fail_once)
    assert client.post("/internal/v1/notifications/email", json=failing, headers=headers).json()["code"] == "NOTIFICATION_UNAVAILABLE"
    monkeypatch.setattr(notification, "send_email", lambda mail: sent.append(mail))
    assert client.post("/internal/v1/notifications/email", json=failing, headers=headers).status_code == 200
    assert len(sent) == 2


def test_payment_mock_ui_contract():
    mock = importlib.import_module("services.payment_mock.app")
    client = TestClient(mock.app)
    now = datetime.now(timezone.utc)
    token = jwt.encode({"sub": "u1", "email": "demo1@example.test", "iss": "ibanking-demo", "aud": "ibanking-api", "iat": now, "exp": now + timedelta(hours=1)}, os.getenv("JWT_SECRET", "development-only-change-this-secret-32-bytes"), algorithm="HS256")
    headers = {"Authorization": "Bearer " + token}
    tuition = client.get("/api/v1/tuition/52600001", headers=headers)
    assert tuition.status_code == 200 and tuition.json()["amount"] == 7000000
    body = {"tuitionId": "HP001", "termsAccepted": True, "requestId": "e677a6b0-8292-4f77-8216-9b39b4e17a87"}
    created = client.post("/api/v1/payments", json=body, headers=headers)
    assert created.status_code == 201 and created.json()["status"] == "PENDING_OTP"
    assert client.post("/api/v1/payments", json=body, headers=headers).status_code == 200
    pid = created.json()["paymentId"]
    assert client.post(f"/api/v1/payments/{pid}/confirm", json={"otp": "000000"}, headers=headers).json()["code"] == "INVALID_OTP"
    assert client.post(f"/api/v1/payments/{pid}/confirm", json={"otp": "123456"}, headers=headers).json()["status"] == "SUCCESS"
    assert client.get("/api/v1/wallet", headers=headers).json()["balance"] == 3000000
