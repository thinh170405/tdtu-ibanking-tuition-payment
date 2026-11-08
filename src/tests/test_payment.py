"""Financial behavior tests against the durable Payment Service, not the mock."""
import importlib
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv("PAYMENT_DATABASE_URL", "sqlite:///" + str(tmp_path / "payment.db"))
    module = importlib.reload(importlib.import_module("services.payment.app"))
    module.Base.metadata.create_all(module.engine)
    with module.SessionLocal.begin() as db:
        db.add_all([module.Wallet(user_id="u1", balance=10000000), module.Wallet(user_id="u2", balance=10000000)])
        db.add_all([module.Student(student_id="52600001", full_name="Sinh viên 1"), module.Student(student_id="52600002", full_name="Sinh viên 2")])
        db.flush()
        db.add_all([module.Tuition(tuition_id="HP001", student_id="52600001", amount=7000000, status="UNPAID"),
                    module.Tuition(tuition_id="HP002", student_id="52600002", amount=7000000, status="UNPAID")])
    messages = []
    monkeypatch.setattr(module, "notify", lambda body: messages.append(body) or True)
    return module, messages


def headers(uid):
    now = datetime.now(timezone.utc)
    token = jwt.encode({"sub": uid, "email": uid + "@example.test", "iss": "ibanking-demo", "aud": "ibanking-api", "iat": now, "exp": now + timedelta(hours=1)}, os.getenv("JWT_SECRET", "development-only-change-this-secret-32-bytes"), algorithm="HS256")
    return {"Authorization": "Bearer " + token}


def create(client, uid, tuition):
    return client.post("/api/v1/payments", headers=headers(uid), json={"tuitionId": tuition, "termsAccepted": True, "requestId": str(uuid4())})


def test_full_payment_otp_and_receipt(setup):
    module, messages = setup
    client = TestClient(module.app)
    created = create(client, "u1", "HP001")
    assert created.status_code == 201
    payment_id = created.json()["paymentId"]
    otp = messages[0]["data"]["otp"]
    assert client.post(f"/api/v1/payments/{payment_id}/confirm", headers=headers("u1"), json={"otp": "bad"}).status_code == 400
    assert client.post(f"/api/v1/payments/{payment_id}/confirm", headers=headers("u1"), json={"otp": "000000" if otp != "000000" else "999999"}).json()["code"] == "INVALID_OTP"
    assert client.get("/api/v1/wallet", headers=headers("u1")).json()["balance"] == 10000000
    result = client.post(f"/api/v1/payments/{payment_id}/confirm", headers=headers("u1"), json={"otp": otp})
    assert result.status_code == 200 and result.json()["status"] == "SUCCESS"
    assert client.post(f"/api/v1/payments/{payment_id}/confirm", headers=headers("u1"), json={"otp": otp}).status_code == 200
    assert client.get("/api/v1/wallet", headers=headers("u1")).json()["balance"] == 3000000
    assert client.get("/api/v1/tuition/52600001", headers=headers("u1")).json()["status"] == "PAID"
    assert client.get("/api/v1/payments", headers=headers("u1")).json()["items"][0]["status"] == "SUCCESS"
    assert [m["type"] for m in messages] == ["OTP", "PAYMENT_SUCCESS"]


def test_same_wallet_concurrent_payments_cannot_overspend(setup):
    module, messages = setup
    client = TestClient(module.app)
    p1 = create(client, "u1", "HP001").json()["paymentId"]
    p2 = create(client, "u1", "HP002").json()["paymentId"]
    codes = {m["data"]["paymentId"]: m["data"]["otp"] for m in messages}
    def confirm(pid):
        return client.post(f"/api/v1/payments/{pid}/confirm", headers=headers("u1"), json={"otp": codes[pid]})
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(confirm, [p1, p2]))
    assert sorted(r.status_code for r in results) == [200, 422]
    assert client.get("/api/v1/wallet", headers=headers("u1")).json()["balance"] == 3000000
    assert sum(client.get(f"/api/v1/payments/{pid}", headers=headers("u1")).json()["status"] == "SUCCESS" for pid in (p1, p2)) == 1


def test_two_wallets_cannot_pay_same_tuition_twice(setup):
    module, messages = setup
    client = TestClient(module.app)
    p1 = create(client, "u1", "HP001").json()["paymentId"]
    p2 = create(client, "u2", "HP001").json()["paymentId"]
    codes = {m["data"]["paymentId"]: m["data"]["otp"] for m in messages}
    def confirm(pair):
        uid, pid = pair
        return client.post(f"/api/v1/payments/{pid}/confirm", headers=headers(uid), json={"otp": codes[pid]})
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(confirm, [("u1", p1), ("u2", p2)]))
    assert sorted(r.status_code for r in results) == [200, 409]
    balances = [client.get("/api/v1/wallet", headers=headers(uid)).json()["balance"] for uid in ("u1", "u2")]
    assert sorted(balances) == [3000000, 10000000]


def test_expired_otp_and_email_failure(setup, monkeypatch):
    module, messages = setup
    client = TestClient(module.app)
    created = create(client, "u1", "HP001")
    pid = created.json()["paymentId"]
    with module.SessionLocal.begin() as db:
        db.get(module.Payment, pid).otp_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.scalar(module.select(module.Otp).where(module.Otp.payment_id == pid)).expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    result = client.post(f"/api/v1/payments/{pid}/confirm", headers=headers("u1"), json={"otp": messages[0]["data"]["otp"]})
    assert result.status_code == 422 and result.json()["code"] == "OTP_EXPIRED"
    assert client.get("/api/v1/wallet", headers=headers("u1")).json()["balance"] == 10000000
    monkeypatch.setattr(module, "notify", lambda body: False)
    result = create(client, "u1", "HP002")
    assert result.status_code == 503
    assert client.get("/api/v1/wallet", headers=headers("u1")).json()["balance"] == 10000000
