import os
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import Depends, FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from services.common import ErrorResponse, StrictModel, error, install_error_handlers


DATABASE_URL = os.getenv("ACCOUNT_DATABASE_URL", "sqlite:///./account-dev.db")
JWT_SECRET = os.getenv("JWT_SECRET", "development-only-change-this-secret-32-bytes")
JWT_ISSUER = os.getenv("JWT_ISSUER", "ibanking-demo")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "ibanking-api")
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "3600"))
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(engine)
hasher = PasswordHasher()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)


class LoginRequest(StrictModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


def session():
    with SessionLocal() as db:
        yield db


def current_user(authorization: str | None = Header(default=None), db: Session = Depends(session)):
    unauthorized = lambda: error(401, "UNAUTHORIZED", "Phiên đăng nhập không hợp lệ.", {"WWW-Authenticate": "Bearer"})
    if not authorization or not authorization.startswith("Bearer "):
        return unauthorized()
    try:
        claims = jwt.decode(authorization[7:], JWT_SECRET, algorithms=["HS256"], issuer=JWT_ISSUER, audience=JWT_AUDIENCE, options={"require": ["sub", "email", "iss", "aud", "iat", "exp"]})
        user = db.get(User, claims["sub"])
        if not user or user.email != claims["email"]:
            return unauthorized()
        return user
    except (jwt.PyJWTError, KeyError):
        return unauthorized()


app = FastAPI(title="iBanking Account Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_ORIGIN], allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])
install_error_handlers(app)


@app.post("/api/v1/auth/login", responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def login(body: LoginRequest, db: Session = Depends(session)):
    user = db.scalar(select(User).where(User.username == body.username))
    try:
        valid = bool(user and hasher.verify(user.password_hash, body.password))
    except (VerifyMismatchError, VerificationError):
        valid = False
    if not valid:
        return error(401, "INVALID_CREDENTIALS", "Tên đăng nhập hoặc mật khẩu không đúng.", {"WWW-Authenticate": "Bearer"})
    now = datetime.now(timezone.utc)
    token = jwt.encode({"sub": user.id, "email": user.email, "iss": JWT_ISSUER, "aud": JWT_AUDIENCE, "iat": now, "exp": now + timedelta(seconds=JWT_TTL_SECONDS)}, JWT_SECRET, algorithm="HS256")
    return {"accessToken": token, "tokenType": "Bearer", "expiresIn": JWT_TTL_SECONDS}


@app.get("/api/v1/users/me", responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def me(user=Depends(current_user)):
    if not isinstance(user, User):
        return user
    return {"userId": user.id, "fullName": user.full_name, "phone": user.phone, "email": user.email}


@app.get("/api/v1/health")
def health():
    return {"status": "UP", "service": "account"}
