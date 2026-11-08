import hashlib
import json
import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Annotated, Literal, Union

from fastapi import FastAPI, Header
from pydantic import EmailStr, Field
from sqlalchemy import DateTime, String, create_engine, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from services.common import ErrorResponse, StrictModel, error, install_error_handlers


DATABASE_URL = os.getenv("NOTIFICATION_DATABASE_URL", "sqlite:///./notification-dev.db")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "development-only-internal-key")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class MessageRecord(Base):
    __tablename__ = "email_messages"
    message_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OtpData(StrictModel):
    paymentId: str = Field(min_length=1, max_length=100)
    otp: str = Field(pattern=r"^[0-9]{6}$")
    expiresAt: datetime


class SuccessData(StrictModel):
    paymentId: str = Field(min_length=1, max_length=100)
    studentId: str = Field(pattern=r"^[0-9]{8}$")
    studentName: str = Field(min_length=1)
    amount: int = Field(gt=0, le=9007199254740991)
    currency: Literal["VND"]
    paidAt: datetime


class OtpRequest(StrictModel):
    messageId: str = Field(min_length=1, max_length=100)
    type: Literal["OTP"]
    to: EmailStr
    data: OtpData


class SuccessRequest(StrictModel):
    messageId: str = Field(min_length=1, max_length=100)
    type: Literal["PAYMENT_SUCCESS"]
    to: EmailStr
    data: SuccessData


NotificationRequest = Annotated[Union[OtpRequest, SuccessRequest], Field(discriminator="type")]


def make_email(body: NotificationRequest) -> EmailMessage:
    mail = EmailMessage()
    mail["From"] = os.getenv("SMTP_FROM", "ibanking@example.test")
    mail["To"] = str(body.to)
    if body.type == "OTP":
        mail["Subject"] = "iBanking - Ma xac thuc giao dich"
        mail.set_content(f"Mã OTP cho giao dịch {body.data.paymentId}: {body.data.otp}\nCó hiệu lực đến {body.data.expiresAt.isoformat()}. Không chia sẻ mã này.")
    else:
        mail["Subject"] = "iBanking - Thanh toan hoc phi thanh cong"
        mail.set_content(f"Giao dịch {body.data.paymentId} đã thanh toán học phí cho {body.data.studentName} ({body.data.studentId}).\nSố tiền: {body.data.amount:,} VND.\nThời gian: {body.data.paidAt.isoformat()}.")
    return mail


def send_email(mail: EmailMessage):
    host = os.getenv("SMTP_HOST")
    if not host:
        raise RuntimeError("SMTP_HOST chưa được cấu hình")
    port = int(os.getenv("SMTP_PORT", "587"))
    security = os.getenv("SMTP_SECURITY", "STARTTLS").upper()
    smtp_class = smtplib.SMTP_SSL if security == "SSL" else smtplib.SMTP
    with smtp_class(host, port, timeout=5) as smtp:
        if security == "STARTTLS":
            smtp.starttls()
        username = os.getenv("SMTP_USERNAME")
        if username:
            smtp.login(username, os.getenv("SMTP_PASSWORD", ""))
        smtp.send_message(mail)


app = FastAPI(title="iBanking Notification Service", version="1.0.0")
install_error_handlers(app)


@app.post("/internal/v1/notifications/email", responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 503: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def notify(body: NotificationRequest, x_internal_key: str | None = Header(default=None)):
    if x_internal_key != INTERNAL_API_KEY:
        return error(403, "FORBIDDEN", "Không có quyền gửi email.")
    payload = body.model_dump(mode="json")
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        row = db.get(MessageRecord, body.messageId)
        if row:
            if row.payload_hash != digest:
                return error(409, "MESSAGE_ID_CONFLICT", "Mã thông điệp đã được dùng cho nội dung khác.")
            if row.status == "SENT":
                return {"messageId": body.messageId, "status": "SENT"}
            if row.status == "PROCESSING" and row.updated_at.replace(tzinfo=timezone.utc) > now - timedelta(seconds=60):
                return error(409, "REQUEST_IN_PROGRESS", "Email đang được xử lý.", {"Retry-After": "1"})
            changed = db.execute(update(MessageRecord).where(MessageRecord.message_id == body.messageId, MessageRecord.payload_hash == digest, MessageRecord.status == row.status, MessageRecord.updated_at == row.updated_at).values(status="PROCESSING", updated_at=now))
            if changed.rowcount != 1:
                db.rollback()
                return error(409, "REQUEST_IN_PROGRESS", "Email đang được xử lý.", {"Retry-After": "1"})
        else:
            db.add(MessageRecord(message_id=body.messageId, payload_hash=digest, status="PROCESSING", updated_at=now))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return error(409, "REQUEST_IN_PROGRESS", "Email đang được xử lý.", {"Retry-After": "1"})
    try:
        send_email(make_email(body))
    except (OSError, smtplib.SMTPException, RuntimeError):
        with SessionLocal.begin() as db:
            row = db.get(MessageRecord, body.messageId)
            row.status = "FAILED"
            row.updated_at = datetime.now(timezone.utc)
        return error(503, "NOTIFICATION_UNAVAILABLE", "Chưa gửi được email. Vui lòng thử lại.")
    with SessionLocal.begin() as db:
        row = db.get(MessageRecord, body.messageId)
        row.status = "SENT"
        row.updated_at = datetime.now(timezone.utc)
    return {"messageId": body.messageId, "status": "SENT"}


@app.get("/api/v1/health")
def health():
    return {"status": "UP", "service": "notification"}
