"""Run T21/T22 against the live Docker PostgreSQL stack; cleans its own test rows."""
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from pathlib import Path
from urllib.parse import quote

import httpx
import jwt
import psycopg

def local_setting(name, default):
    path = Path(__file__).resolve().parents[1] / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip()
    return default


DB = os.getenv("PAYMENT_TEST_DSN", "postgresql://ibanking:" + quote(local_setting("POSTGRES_PASSWORD", "local-demo-password")) + "@localhost:5433/ibanking_payment")
BASE = os.getenv("PAYMENT_TEST_URL", "http://localhost:8082/api/v1")
MAIL = os.getenv("MAILPIT_TEST_URL", "http://localhost:8025/api/v1")
SECRET = os.getenv("JWT_SECRET", local_setting("JWT_SECRET", "local-demo-secret-at-least-32-bytes-long"))
USERS = ["t21u", "t22u1", "t22u2"]
TUITION = ["T21A", "T21B", "T22A"]
STUDENTS = ["99000001", "99000002", "99000003"]


def cleanup():
    with psycopg.connect(DB) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM email_jobs WHERE payment_id IN (SELECT payment_id FROM payments WHERE tuition_id = ANY(%s))", (TUITION,))
            cur.execute("DELETE FROM otps WHERE payment_id IN (SELECT payment_id FROM payments WHERE tuition_id = ANY(%s))", (TUITION,))
            cur.execute("DELETE FROM payments WHERE tuition_id = ANY(%s)", (TUITION,))
            cur.execute("DELETE FROM tuitions WHERE tuition_id = ANY(%s)", (TUITION,))
            cur.execute("DELETE FROM students WHERE student_id = ANY(%s)", (STUDENTS,))
            cur.execute("DELETE FROM wallets WHERE user_id = ANY(%s)", (USERS,))


def seed():
    with psycopg.connect(DB) as conn:
        with conn.cursor() as cur:
            for uid in USERS:
                cur.execute("INSERT INTO wallets(user_id,balance,currency) VALUES(%s,10000000,'VND')", (uid,))
            for sid, tid in zip(STUDENTS, TUITION):
                cur.execute("INSERT INTO students(student_id,full_name) VALUES(%s,%s)", (sid, "Concurrency test"))
                cur.execute("INSERT INTO tuitions(tuition_id,student_id,amount,status) VALUES(%s,%s,7000000,'UNPAID')", (tid, sid))


def auth(uid):
    now = datetime.now(timezone.utc)
    token = jwt.encode({"sub": uid, "email": uid + "@example.com", "iss": "ibanking-demo", "aud": "ibanking-api", "iat": now, "exp": now + timedelta(hours=1)}, SECRET, algorithm="HS256")
    return {"Authorization": "Bearer " + token}


def create(uid, tuition):
    r = httpx.post(BASE + "/payments", headers=auth(uid), json={"tuitionId": tuition, "termsAccepted": True, "requestId": str(uuid4())}, timeout=15)
    assert r.status_code == 201, r.text
    return r.json()["paymentId"]


def otp_for(pid):
    for _ in range(20):
        messages = httpx.get(MAIL + "/messages").json()["messages"]
        for message in messages:
            data = httpx.get(MAIL + "/message/" + message["ID"]).json()
            if pid in data.get("Text", "") and "OTP" in data.get("Text", ""):
                return re.search(r"(?<!\d)\d{6}(?!\d)", data["Text"]).group()
        time.sleep(0.25)
    raise AssertionError("OTP email missing for " + pid)


def confirm(pair):
    uid, pid, otp = pair
    return httpx.post(BASE + "/payments/" + pid + "/confirm", headers=auth(uid), json={"otp": otp}, timeout=15)


def main():
    cleanup()
    seed()
    try:
        p1, p2 = create("t21u", "T21A"), create("t21u", "T21B")
        with ThreadPoolExecutor(max_workers=2) as pool:
            r = list(pool.map(confirm, [("t21u", p1, otp_for(p1)), ("t21u", p2, otp_for(p2))]))
        assert sorted(x.status_code for x in r) == [200, 422], [x.text for x in r]
        assert httpx.get(BASE + "/wallet", headers=auth("t21u")).json()["balance"] == 3000000
        print("T21 PASS: one success, one insufficient balance, wallet 3,000,000 VND")

        p3, p4 = create("t22u1", "T22A"), create("t22u2", "T22A")
        with ThreadPoolExecutor(max_workers=2) as pool:
            r = list(pool.map(confirm, [("t22u1", p3, otp_for(p3)), ("t22u2", p4, otp_for(p4))]))
        assert sorted(x.status_code for x in r) == [200, 409], [x.text for x in r]
        balances = [httpx.get(BASE + "/wallet", headers=auth(uid)).json()["balance"] for uid in ("t22u1", "t22u2")]
        assert sorted(balances) == [3000000, 10000000]
        print("T22 PASS: one success, one already paid, only winning wallet debited")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
