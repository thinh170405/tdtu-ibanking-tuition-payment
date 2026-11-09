"""Create payment schema and idempotently load the demo data."""
import json
from pathlib import Path

from datetime import datetime

from services.payment.app import Base, Payment, SessionLocal, Student, Tuition, Wallet, engine


def main():
    Base.metadata.create_all(engine)
    root = Path(__file__).resolve().parents[2]
    source = root / "data" / "demo-base.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    extra_path = root / "data" / "demo-extra.json"
    if extra_path.exists():
        extra = json.loads(extra_path.read_text(encoding="utf-8"))
        for key in ("wallets", "students", "tuitions", "payments"):
            data[key].extend(extra[key])
    with SessionLocal.begin() as db:
        for row in data["wallets"]:
            if not db.get(Wallet, row["userId"]):
                db.add(Wallet(user_id=row["userId"], balance=row["balance"], currency=row["currency"]))
        for row in data["students"]:
            if not db.get(Student, row["studentId"]):
                db.add(Student(student_id=row["studentId"], full_name=row["studentName"]))
        db.flush()
        for row in data["tuitions"]:
            if not db.get(Tuition, row["tuitionId"]):
                db.add(Tuition(tuition_id=row["tuitionId"], student_id=row["studentId"], amount=row["amount"], status=row["status"], paid_at=datetime.fromisoformat(row["paidAt"].replace("Z", "+00:00")) if row.get("paidAt") else None))
        db.flush()
        for row in data.get("payments", []):
            if not db.get(Payment, row["paymentId"]):
                db.add(Payment(payment_id=row["paymentId"], user_id=row["userId"], tuition_id=row["tuitionId"],
                               request_id=row["requestId"], amount=row["amount"], status=row["status"],
                               created_at=datetime.fromisoformat(row["createdAt"].replace("Z", "+00:00")),
                               otp_expires_at=datetime.fromisoformat(row["otpExpiresAt"].replace("Z", "+00:00")) if row.get("otpExpiresAt") else None,
                               paid_at=datetime.fromisoformat(row["paidAt"].replace("Z", "+00:00")) if row.get("paidAt") else None,
                               failure_code=row.get("failureCode")))
    print("Payment seed complete.")


if __name__ == "__main__":
    main()
