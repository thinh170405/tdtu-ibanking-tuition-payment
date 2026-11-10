"""Payment API with durable OTP and atomic financial updates."""
import hashlib
import hmac
import os
import re
import secrets
import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import httpx
import jwt
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import Field
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, create_engine, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from services.common import StrictModel, error, install_error_handlers

DATABASE_URL = os.getenv("PAYMENT_DATABASE_URL", "sqlite:///./payment-dev.db")
JWT_SECRET = os.getenv("JWT_SECRET", "development-only-change-this-secret-32-bytes")
JWT_ISSUER = os.getenv("JWT_ISSUER", "ibanking-demo")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "ibanking-api")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "development-only-internal-key")
NOTIFICATION_URL = os.getenv("NOTIFICATION_URL", "http://localhost:8083")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 30} if DATABASE_URL.startswith("sqlite") else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = "wallets"
    __table_args__ = (CheckConstraint("balance >= 0", name="wallet_nonnegative"),)
    user_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    balance: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="VND", nullable=False)


class Student(Base):
    __tablename__ = "students"
    student_id: Mapped[str] = mapped_column(String(8), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)


class Tuition(Base):
    __tablename__ = "tuitions"
    __table_args__ = (CheckConstraint("amount > 0", name="tuition_positive"),)
    tuition_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.student_id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(12), default="UNPAID", nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    student: Mapped[Student] = relationship()


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (UniqueConstraint("user_id", "request_id", name="uq_payment_request"),)
    payment_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    tuition_id: Mapped[str] = mapped_column(ForeignKey("tuitions.tuition_id"), nullable=False)
    request_id: Mapped[str] = mapped_column(String(36), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_code: Mapped[str | None] = mapped_column(String(40))
    tuition: Mapped[Tuition] = relationship()


class Otp(Base):
    __tablename__ = "otps"
    otp_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    payment_id: Mapped[str] = mapped_column(ForeignKey("payments.payment_id"), unique=True, nullable=False)
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class EmailJob(Base):
    __tablename__ = "email_jobs"
    job_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    payment_id: Mapped[str] = mapped_column(ForeignKey("payments.payment_id"), unique=True, nullable=False)
    email_to: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class CreateBody(StrictModel):
    tuitionId: str = Field(min_length=1, max_length=100)
    termsAccepted: bool
    requestId: UUID


class ConfirmBody(StrictModel):
    otp: str = Field(pattern=r"^[0-9]{6}$")


def retry_pending_receipts():
    with SessionLocal() as db:
        ids = db.scalars(select(EmailJob.payment_id).where(EmailJob.status == "PENDING").limit(50)).all()
    for payment_id in ids:
        try:
            send_receipt(payment_id)
        except Exception:
            pass


@asynccontextmanager
async def lifespan(_app):
    async def worker():
        while True:
            await asyncio.sleep(30)
            await asyncio.to_thread(retry_pending_receipts)
    task = asyncio.create_task(worker())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="iBanking Payment Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_ORIGIN], allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])
install_error_handlers(app)


def now_utc():
    return datetime.now(timezone.utc)


def aware(value):
    return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value


def iso(value):
    return aware(value).isoformat().replace("+00:00", "Z") if value else None


def actor(authorization):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        claims = jwt.decode(authorization[7:], JWT_SECRET, algorithms=["HS256"], issuer=JWT_ISSUER, audience=JWT_AUDIENCE, options={"require": ["sub", "email", "iss", "aud", "iat", "exp"]})
        return claims
    except (jwt.PyJWTError, KeyError):
        return None


def auth_error():
    return error(401, "UNAUTHORIZED", "Vui lòng đăng nhập.", {"WWW-Authenticate": "Bearer"})


def public(db, payment):
    tuition = db.get(Tuition, payment.tuition_id)
    student = db.get(Student, tuition.student_id)
    return {"paymentId": payment.payment_id, "tuitionId": payment.tuition_id, "studentId": student.student_id,
            "studentName": student.full_name, "amount": payment.amount, "currency": "VND", "status": payment.status,
            "createdAt": iso(payment.created_at), "otpExpiresAt": iso(payment.otp_expires_at), "paidAt": iso(payment.paid_at),
            "failureCode": payment.failure_code}


def otp_hash(payment_id, code):
    # A stable fingerprint lets creation reject a code active for another payment.
    # Verification still loads the OTP by payment_id first.
    return hmac.new(JWT_SECRET.encode(), code.encode(), hashlib.sha256).hexdigest()


def new_otp_code(db, now, old_hash=None):
    for _ in range(20):
        candidate = f"{secrets.randbelow(1000000):06d}"
        digest = otp_hash("", candidate)
        if digest == old_hash:
            continue
        active = db.scalar(select(Otp).join(Payment, Otp.payment_id == Payment.payment_id).where(
            Payment.status == "PENDING_OTP", Otp.expires_at > now, Otp.code_hash == digest))
        if not active:
            return candidate
    return None


def notify(payload):
    try:
        response = httpx.post(NOTIFICATION_URL.rstrip("/") + "/internal/v1/notifications/email", json=payload,
                              headers={"X-Internal-Key": INTERNAL_API_KEY}, timeout=6.0)
        return response.status_code == 200
    except httpx.RequestError:
        return False


def send_receipt(payment_id):
    with SessionLocal() as db:
        job = db.scalar(select(EmailJob).where(EmailJob.payment_id == payment_id))
        payment = db.get(Payment, payment_id)
        if not job or not payment or job.status == "SENT":
            return
        details = public(db, payment)
        payload = {"messageId": "success:" + payment_id, "type": "PAYMENT_SUCCESS", "to": job.email_to,
                   "data": {"paymentId": payment_id, "studentId": details["studentId"], "studentName": details["studentName"],
                            "amount": payment.amount, "currency": "VND", "paidAt": details["paidAt"]}}
    sent = notify(payload)
    with SessionLocal.begin() as db:
        job = db.scalar(select(EmailJob).where(EmailJob.payment_id == payment_id).with_for_update())
        if job and job.status != "SENT":
            job.attempts += 1
            job.status = "SENT" if sent else "PENDING"


@app.get("/api/v1/health")
def health():
    return {"status": "UP", "service": "payment"}


@app.get("/api/v1/wallet")
def wallet(authorization: str | None = Header(default=None)):
    claims = actor(authorization)
    if not claims: return auth_error()
    with SessionLocal() as db:
        row = db.get(Wallet, claims["sub"])
        if not row: return error(404, "WALLET_NOT_FOUND", "Không tìm thấy ví.")
        return {"userId": row.user_id, "balance": row.balance, "currency": row.currency}


@app.get("/api/v1/tuition/{mssv}")
def tuition(mssv: str, authorization: str | None = Header(default=None)):
    if not actor(authorization): return auth_error()
    if not re.fullmatch(r"[0-9]{8}", mssv): return error(400, "VALIDATION_ERROR", "MSSV phải gồm 8 chữ số.")
    with SessionLocal() as db:
        student = db.get(Student, mssv)
        if not student: return error(404, "STUDENT_NOT_FOUND", "Không tìm thấy sinh viên.")
        row = db.scalar(select(Tuition).where(Tuition.student_id == mssv).order_by(Tuition.tuition_id))
        if not row: return error(404, "TUITION_NOT_FOUND", "Không tìm thấy khoản học phí.")
        return {"studentId": mssv, "studentName": student.full_name, "tuitionId": row.tuition_id,
                "amount": row.amount, "currency": "VND", "status": row.status, "paidAt": iso(row.paid_at)}


@app.post("/api/v1/payments")
def create(body: CreateBody, authorization: str | None = Header(default=None)):
    claims = actor(authorization)
    if not claims: return auth_error()
    if body.termsAccepted is not True: return error(400, "VALIDATION_ERROR", "Cần đồng ý điều khoản.")
    uid = claims["sub"]
    request_id = str(body.requestId)
    code = None
    with SessionLocal() as db:
        previous = db.scalar(select(Payment).where(Payment.user_id == uid, Payment.request_id == request_id))
        if previous:
            if previous.tuition_id != body.tuitionId: return error(409, "REQUEST_ID_CONFLICT", "Mã yêu cầu đã dùng cho khoản khác.")
            return public(db, previous)
        wallet_row = db.get(Wallet, uid)
        tuition_row = db.get(Tuition, body.tuitionId)
        if not wallet_row: return error(404, "WALLET_NOT_FOUND", "Không tìm thấy ví.")
        if not tuition_row: return error(404, "TUITION_NOT_FOUND", "Không tìm thấy học phí.")
        if tuition_row.status != "UNPAID": return error(409, "TUITION_ALREADY_PAID", "Học phí đã thanh toán.")
        if wallet_row.balance < tuition_row.amount: return error(422, "INSUFFICIENT_BALANCE", "Số dư không đủ.")
        now = now_utc()
        payment_id = "pay_" + uuid4().hex
        code = new_otp_code(db, now)
        if code is None: return error(500, "INTERNAL_ERROR", "Không tạo được OTP.")
        expires = now + timedelta(minutes=5)
        payment = Payment(payment_id=payment_id, user_id=uid, tuition_id=body.tuitionId, request_id=request_id,
                          amount=tuition_row.amount, status="PENDING_OTP", created_at=now, otp_expires_at=expires)
        try:
            db.add(payment)
            db.flush()
            db.add(Otp(otp_id="otp_" + uuid4().hex, payment_id=payment_id, code_hash=otp_hash(payment_id, code), issued_at=now, expires_at=expires))
            db.commit()
        except IntegrityError:
            db.rollback()
            return error(409, "REQUEST_IN_PROGRESS", "Yêu cầu đang được xử lý.", {"Retry-After": "1"})
        result = public(db, payment)
    delivered = notify({"messageId": "otp:" + payment_id, "type": "OTP", "to": claims["email"],
                        "data": {"paymentId": payment_id, "otp": code, "expiresAt": iso(expires)}})
    if not delivered:
        with SessionLocal.begin() as db:
            payment = db.get(Payment, payment_id)
            payment.status = "FAILED"
            payment.failure_code = "NOTIFICATION_UNAVAILABLE"
        return error(503, "NOTIFICATION_UNAVAILABLE", "Chưa gửi được OTP.")
    return JSONResponse(status_code=201, content=result)


@app.post("/api/v1/payments/{payment_id}/resend-otp")
def resend_otp(payment_id: str, authorization: str | None = Header(default=None)):
    claims = actor(authorization)
    if not claims: return auth_error()
    try:
        with SessionLocal() as db:
            if DATABASE_URL.startswith("sqlite"):
                db.connection().exec_driver_sql("BEGIN IMMEDIATE")
            row = db.scalar(select(Payment).where(Payment.payment_id == payment_id).with_for_update())
            if not row: return error(404, "PAYMENT_NOT_FOUND", "Không tìm thấy giao dịch.")
            if row.user_id != claims["sub"]: return error(403, "FORBIDDEN", "Không có quyền gửi lại OTP.")
            if row.status not in ("PENDING_OTP", "EXPIRED"):
                return error(409, "PAYMENT_NOT_PENDING", "Giao dịch không còn chờ OTP.")
            otp = db.scalar(select(Otp).where(Otp.payment_id == payment_id).with_for_update())
            if not otp or otp.used_at:
                return error(409, "PAYMENT_NOT_PENDING", "Giao dịch không còn chờ OTP.")
            now = now_utc()
            wait_seconds = 30 - (now - aware(otp.issued_at)).total_seconds()
            if wait_seconds > 0:
                return error(409, "OTP_RESEND_TOO_SOON", "Vui lòng đợi trước khi gửi lại OTP.",
                             {"Retry-After": str(max(1, int(wait_seconds) + 1))})
            wallet_row = db.scalar(select(Wallet).where(Wallet.user_id == row.user_id).with_for_update())
            tuition_row = db.scalar(select(Tuition).where(Tuition.tuition_id == row.tuition_id).with_for_update())
            if not tuition_row or tuition_row.status != "UNPAID":
                row.status, row.failure_code = "FAILED", "TUITION_ALREADY_PAID"
                db.commit()
                return error(409, "TUITION_ALREADY_PAID", "Học phí đã thanh toán.")
            if not wallet_row or wallet_row.balance < row.amount:
                row.status, row.failure_code = "FAILED", "INSUFFICIENT_BALANCE"
                db.commit()
                return error(422, "INSUFFICIENT_BALANCE", "Số dư không đủ.")
            code = new_otp_code(db, now, otp.code_hash)
            if code is None: return error(500, "INTERNAL_ERROR", "Không tạo được OTP.")
            expires = now + timedelta(minutes=5)
            otp.otp_id = "otp_" + uuid4().hex
            otp.code_hash, otp.issued_at, otp.expires_at = otp_hash(payment_id, code), now, expires
            row.otp_expires_at, row.status, row.failure_code = expires, "PENDING_OTP", None
            message_id = "otp:" + payment_id + ":" + otp.otp_id
            db.commit()
            result = public(db, row)
        delivered = notify({"messageId": message_id, "type": "OTP", "to": claims["email"],
                            "data": {"paymentId": payment_id, "otp": code, "expiresAt": iso(expires)}})
        if not delivered:
            return error(503, "NOTIFICATION_UNAVAILABLE", "Chưa gửi được OTP. Vui lòng thử lại sau.")
        return result
    except OperationalError:
        return error(409, "REQUEST_IN_PROGRESS", "Giao dịch đang được xử lý.", {"Retry-After": "1"})


@app.get("/api/v1/payments")
def listing(authorization: str | None = Header(default=None)):
    claims = actor(authorization)
    if not claims: return auth_error()
    with SessionLocal() as db:
        rows = db.scalars(select(Payment).where(Payment.user_id == claims["sub"]).order_by(Payment.created_at.desc(), Payment.payment_id)).all()
        return {"items": [public(db, row) for row in rows]}


@app.get("/api/v1/payments/{payment_id}")
def detail(payment_id: str, authorization: str | None = Header(default=None)):
    claims = actor(authorization)
    if not claims: return auth_error()
    with SessionLocal() as db:
        row = db.get(Payment, payment_id)
        if not row: return error(404, "PAYMENT_NOT_FOUND", "Không tìm thấy giao dịch.")
        if row.user_id != claims["sub"]: return error(403, "FORBIDDEN", "Không có quyền xem giao dịch.")
        return public(db, row)


@app.post("/api/v1/payments/{payment_id}/confirm")
def confirm(payment_id: str, body: ConfirmBody, authorization: str | None = Header(default=None)):
    claims = actor(authorization)
    if not claims: return auth_error()
    try:
        with SessionLocal() as db:
            if DATABASE_URL.startswith("sqlite"):
                db.connection().exec_driver_sql("BEGIN IMMEDIATE")
            row = db.scalar(select(Payment).where(Payment.payment_id == payment_id).with_for_update())
            if not row: return error(404, "PAYMENT_NOT_FOUND", "Không tìm thấy giao dịch.")
            if row.user_id != claims["sub"]: return error(403, "FORBIDDEN", "Không có quyền xác nhận giao dịch.")
            if row.status == "SUCCESS": return public(db, row)
            if row.status != "PENDING_OTP": return error(409, "TUITION_ALREADY_PAID" if row.failure_code == "TUITION_ALREADY_PAID" else "OTP_DELIVERY_PENDING", "Giao dịch không còn chờ OTP.")
            otp = db.scalar(select(Otp).where(Otp.payment_id == payment_id).with_for_update())
            now = now_utc()
            if not otp or otp.used_at: return error(422, "INVALID_OTP", "OTP không hợp lệ.")
            if now >= aware(otp.expires_at):
                row.status, row.failure_code = "EXPIRED", "OTP_EXPIRED"
                db.commit()
                return error(422, "OTP_EXPIRED", "OTP đã hết hạn.")
            if not hmac.compare_digest(otp.code_hash, otp_hash(payment_id, body.otp)):
                return error(422, "INVALID_OTP", "OTP không đúng.")
            wallet_row = db.scalar(select(Wallet).where(Wallet.user_id == row.user_id).with_for_update())
            tuition_row = db.scalar(select(Tuition).where(Tuition.tuition_id == row.tuition_id).with_for_update())
            if not wallet_row: return error(404, "WALLET_NOT_FOUND", "Không tìm thấy ví.")
            if tuition_row.status != "UNPAID":
                row.status, row.failure_code = "FAILED", "TUITION_ALREADY_PAID"
                db.commit()
                return error(409, "TUITION_ALREADY_PAID", "Học phí đã thanh toán.")
            if wallet_row.balance < row.amount:
                row.status, row.failure_code = "FAILED", "INSUFFICIENT_BALANCE"
                db.commit()
                return error(422, "INSUFFICIENT_BALANCE", "Số dư không đủ.")
            wallet_row.balance -= row.amount
            tuition_row.status, tuition_row.paid_at = "PAID", now
            row.status, row.paid_at = "SUCCESS", now
            otp.used_at = now
            db.add(EmailJob(job_id="email_" + uuid4().hex, payment_id=payment_id, email_to=claims["email"], status="PENDING", attempts=0))
            db.commit()
            result = public(db, row)
        try:
            send_receipt(payment_id)
        except Exception:
            # The committed payment remains successful; the durable email job is retryable.
            pass
        return result
    except OperationalError:
        return error(409, "REQUEST_IN_PROGRESS", "Giao dịch đang được xử lý.", {"Retry-After": "1"})
