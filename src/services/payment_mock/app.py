"""Payment mock dành riêng cho gói A. Không dùng làm bằng chứng tài chính."""
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
import os
import jwt

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import Field

from services.common import StrictModel, error, install_error_handlers

app = FastAPI(title="Payment mock for A")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])
install_error_handlers(app)
wallets = {"u1": 10000000, "u2": 10000000}
students = {
    "52600001": ("Nguyễn Văn An", "HP001", 7000000, "UNPAID"),
    "52600002": ("Trần Thị Bình", "HP002", 7000000, "UNPAID"),
    "52600003": ("Lê Minh Chi", "HP003", 5000000, "PAID"),
    "52600004": ("Phạm Quốc Dũng", "HP004", 11000000, "UNPAID"),
    "52600005": ("Võ Thu Giang", "HP005", 10000000, "UNPAID"),
    "52600006": ("Đặng Ngọc Hà", None, None, None),
}
payments = {}
request_ids = {}


def owner(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        claims = jwt.decode(authorization[7:], os.getenv("JWT_SECRET", "development-only-change-this-secret-32-bytes"), algorithms=["HS256"], issuer="ibanking-demo", audience="ibanking-api")
        return claims["sub"]
    except (jwt.PyJWTError, KeyError):
        return None


def auth(authorization):
    return error(401, "UNAUTHORIZED", "Vui lòng đăng nhập.", {"WWW-Authenticate": "Bearer"}) if not owner(authorization) else None


class CreateBody(StrictModel):
    tuitionId: str = Field(min_length=1, max_length=100)
    termsAccepted: bool
    requestId: UUID


class ConfirmBody(StrictModel):
    otp: str = Field(pattern=r"^[0-9]{6}$")


@app.get("/api/v1/health")
def health():
    return {"status": "UP", "service": "payment"}


@app.get("/api/v1/wallet")
def wallet(authorization: str | None = Header(default=None)):
    if fail := auth(authorization): return fail
    return {"userId": owner(authorization), "balance": wallets[owner(authorization)], "currency": "VND"}


@app.get("/api/v1/tuition/{mssv}")
def tuition(mssv: str, authorization: str | None = Header(default=None)):
    if fail := auth(authorization): return fail
    if len(mssv) != 8 or not mssv.isascii() or not mssv.isdigit(): return error(400, "VALIDATION_ERROR", "MSSV phải gồm 8 chữ số.")
    if mssv not in students: return error(404, "STUDENT_NOT_FOUND", "Không tìm thấy sinh viên.")
    name, tid, amount, status = students[mssv]
    if not tid: return error(404, "TUITION_NOT_FOUND", "Sinh viên chưa có khoản học phí.")
    return {"studentId": mssv, "studentName": name, "tuitionId": tid, "amount": amount, "currency": "VND", "status": status, "paidAt": None}


@app.post("/api/v1/payments")
def create(body: CreateBody, authorization: str | None = Header(default=None)):
    if fail := auth(authorization): return fail
    if not body.termsAccepted: return error(400, "VALIDATION_ERROR", "Cần đồng ý điều khoản.")
    uid = owner(authorization)
    key = (uid, body.requestId)
    if key in request_ids:
        old = payments[request_ids[key]]
        if old["public"]["tuitionId"] != body.tuitionId: return error(409, "REQUEST_ID_CONFLICT", "Mã yêu cầu đã dùng cho khoản khác.")
        return old["public"]
    entry = next(((sid, data) for sid, data in students.items() if data[1] == body.tuitionId), None)
    if not entry: return error(404, "TUITION_NOT_FOUND", "Không tìm thấy học phí.")
    sid, (name, tid, amount, status) = entry
    if status == "PAID": return error(409, "TUITION_ALREADY_PAID", "Học phí đã thanh toán.")
    if wallets[uid] < amount: return error(422, "INSUFFICIENT_BALANCE", "Số dư không đủ.")
    now = datetime.now(timezone.utc)
    payment = {"paymentId": "pay_" + uuid4().hex, "tuitionId": tid, "studentId": sid, "studentName": name, "amount": amount, "currency": "VND", "status": "PENDING_OTP", "createdAt": now.isoformat().replace("+00:00", "Z"), "otpExpiresAt": (now + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"), "paidAt": None, "failureCode": None}
    payments[payment["paymentId"]] = {"owner": uid, "public": payment}
    request_ids[key] = payment["paymentId"]
    return JSONResponse(status_code=201, content=payment)


@app.get("/api/v1/payments")
def listing(authorization: str | None = Header(default=None)):
    if fail := auth(authorization): return fail
    return {"items": sorted((p["public"] for p in payments.values() if p["owner"] == owner(authorization)), key=lambda p: p["createdAt"], reverse=True)}


@app.get("/api/v1/payments/{payment_id}")
def detail(payment_id: str, authorization: str | None = Header(default=None)):
    if fail := auth(authorization): return fail
    record = payments.get(payment_id)
    return record["public"] if record and record["owner"] == owner(authorization) else error(404, "PAYMENT_NOT_FOUND", "Không tìm thấy giao dịch.")


@app.post("/api/v1/payments/{payment_id}/confirm")
def confirm(payment_id: str, body: ConfirmBody, authorization: str | None = Header(default=None)):
    if fail := auth(authorization): return fail
    record = payments.get(payment_id)
    if not record or record["owner"] != owner(authorization): return error(404, "PAYMENT_NOT_FOUND", "Không tìm thấy giao dịch.")
    payment = record["public"]
    if payment["status"] == "SUCCESS": return payment
    if datetime.now(timezone.utc) >= datetime.fromisoformat(payment["otpExpiresAt"].replace("Z", "+00:00")):
        payment["status"], payment["failureCode"] = "EXPIRED", "OTP_EXPIRED"
        return error(422, "OTP_EXPIRED", "OTP đã hết hạn.")
    if body.otp != "123456": return error(422, "INVALID_OTP", "OTP không đúng. Mock dùng 123456.")
    payment["status"] = "SUCCESS"
    payment["paidAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    wallets[owner(authorization)] -= payment["amount"]
    sid = payment["studentId"]
    name, tid, amount, _ = students[sid]
    students[sid] = (name, tid, amount, "PAID")
    return payment
