# Hướng dẫn gói A — iBanking

## Thành phần và trạng thái

- `services/account`: FastAPI, tài khoản, JWT, migration/seed; SQLite mặc định khi phát triển, PostgreSQL qua `ACCOUNT_DATABASE_URL`.
- `services/notification`: FastAPI, gửi SMTP, lưu `messageId`/trạng thái; PostgreSQL qua `NOTIFICATION_DATABASE_URL`.
- `services/payment_mock`: mock cho UI, OTP cố định `123456`; chỉ dùng khi A làm riêng.
- `frontend`: React + Vite. Đọc API URL từ `VITE_ACCOUNT_API_BASE_URL` và `VITE_PAYMENT_API_BASE_URL`.
- `docs/architecture.md`: Use Case, kiến trúc và luồng.
- `../cau-hinh-chung/contract/`: hợp đồng API, seed và ma trận test do nhóm cung cấp.

## Chạy local

Yêu cầu Python 3.11+, Node 24+; chạy lệnh tại thư mục `src`:

```powershell
python -m pip install -r requirements-A.txt
$env:PYTHONIOENCODING='utf-8'
$env:JWT_SECRET='replace-this-with-a-random-secret-at-least-32-bytes'
$env:INTERNAL_API_KEY='replace-this-with-a-separate-random-key'
python -m services.account.seed
python -m services.notification.init_db
```

Mở bốn terminal:

```powershell
python -m uvicorn services.account.app:app --port 8081
python -m uvicorn services.notification.app:app --port 8083
python -m uvicorn services.payment_mock.app:app --port 8089
cd frontend; npm install; Copy-Item .env.example .env; npm run dev
```

Mở `http://localhost:5173`, đăng nhập `demo1` / `Demo!2026`. MSSV thử: `52600001` (7 triệu), `52600003` (đã đóng), `52600004` (thiếu tiền), `52600005` (bằng số dư). Trong mock, OTP là `123456`; mock không gửi email và không bảo đảm dữ liệu tài chính.

## Chạy bằng Docker Compose

Sao chép `.env.example` thành `src/.env`, rồi thay `JWT_SECRET` bằng khóa ngẫu nhiên ít nhất 32 byte, đặt `INTERNAL_API_KEY` riêng và cấu hình SMTP. Nếu chưa cấu hình SMTP, Notification trả `503 NOTIFICATION_UNAVAILABLE` khi được gọi; UI với Payment mock vẫn chạy vì mock không gửi mail.

```powershell
docker compose -f compose-A.yaml up --build
```

Compose chạy Account và Notification trên PostgreSQL riêng database, Payment mock 8089 và UI 5173. Cổng PostgreSQL trên host là 5433. Khi thay email demo, cập nhật `DEMO_EMAIL_1/2`, chạy lại seed và đăng nhập lại để JWT chứa email mới.

## Ghép Payment thật của B

1. Đổi `VITE_PAYMENT_API_BASE_URL` thành `http://localhost:8082/api/v1`; restart Vite hoặc build lại frontend.
2. Đồng bộ `JWT_SECRET`, `JWT_ISSUER=ibanking-demo`, `JWT_AUDIENCE=ibanking-api` giữa Account và Payment. Payment phải kiểm tra JWT, không dùng cách xác thực giả của mock.
3. Payment gọi Notification bằng `http://notification:8083` trong Compose hoặc `http://localhost:8083` khi chạy local, dùng cùng `INTERNAL_API_KEY`.
4. Cấu hình SMTP thật và email demo do nhóm kiểm soát; đăng nhập lại.
5. Chạy login → wallet → tra cứu → tạo payment → OTP email → confirm → đọc lại wallet/tuition/history → email xác nhận. Sau đó chạy hai test concurrency của B. Không dùng mock trong demo tích hợp.

## Kiểm thử phần A

```powershell
python -m pytest tests/test_a.py -q
cd frontend; npm run build
```

Các kiểm thử hiện có xác nhận login, hồ sơ, JWT thiếu, validation, khóa nội bộ, gửi email một lần theo `messageId`, xung đột nội dung, retry sau lỗi SMTP và luồng với Payment mock. Kiểm tra email đến inbox và toàn luồng thật chỉ có thể thực hiện sau khi cấu hình SMTP và ghép Payment B.

## API và dữ liệu

Account: `POST /api/v1/auth/login`, `GET /api/v1/users/me`, `GET /api/v1/health`.

Notification: `POST /internal/v1/notifications/email`, `GET /api/v1/health`.

API docs tự sinh: `http://localhost:8081/docs`, `http://localhost:8083/docs`. Hợp đồng tổng: `../cau-hinh-chung/contract/.../01-openapi.json`. Lỗi validation theo hợp đồng là `400 {"code":"VALIDATION_ERROR","message":"..."}`.
