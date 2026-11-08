# Phân hệ đóng học phí iBanking

## Chạy toàn bộ hệ thống

Yêu cầu Docker Desktop. Tại thư mục `src`, chạy:

```powershell
docker compose -f compose.yaml up --build -d
docker compose -f compose.yaml ps
```

Mở giao diện tại http://localhost:5173. Đăng nhập `demo1` / `Demo!2026`. Hộp thư thử Mailpit tại http://localhost:8025 nhận OTP và email xác nhận. Dữ liệu mẫu dùng MSSV `52600001` (7 triệu), `52600002` (7 triệu), `52600003` (đã trả), `52600004` (11 triệu, thiếu số dư với ví 10 triệu), `52600005` (10 triệu). Có thể trả học phí cho sinh viên khác. Account, Payment, Notification lần lượt ở cổng 8081, 8082, 8083; PostgreSQL host 5433. Email demo mặc định dùng `example.com` vì bộ kiểm tra địa chỉ từ chối `.test`; Mailpit giữ thư trong nội bộ.

File `compose.yaml` dùng mật khẩu và khóa **chỉ cho môi trường demo local**. Khi triển khai ngoài máy cá nhân, đặt `POSTGRES_PASSWORD`, `JWT_SECRET`, `INTERNAL_API_KEY` riêng trong `.env` và dùng HTTPS. Mặc định SMTP dùng Mailpit; nếu `.env` có `SMTP_HOST`, `SMTP_PORT`, `SMTP_SECURITY`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`, Notification sẽ gửi qua SMTP đó. Mailpit là hộp thư thử trong Docker; email ở đó không được gửi ra Internet.

## Luồng sử dụng

1. Đăng nhập và xem hồ sơ, số dư.
2. Nhập MSSV 8 chữ số, kiểm tra sinh viên, số tiền và trạng thái học phí.
3. Đồng ý điều khoản và chọn thanh toán toàn bộ.
4. Mở Mailpit, đọc OTP mới nhất, nhập mã trong vòng 5 phút.
5. Kiểm tra kết quả, số dư, học phí, lịch sử và email xác nhận trong Mailpit.

## Cấu trúc và API

- `services/account`: `users`, đăng nhập và hồ sơ; phát JWT.
- `services/payment`: `wallets`, `students`, `tuitions`, `payments`, `otps`, `email_jobs`; kiểm tra OTP, thanh toán và xử lý đồng thời trong database transaction.
- `services/notification`: `email_messages`, gửi và chống gửi trùng qua SMTP.
- `frontend`: React; gọi Account và Payment bằng Bearer JWT.
- Hợp đồng API và danh sách mã lỗi: `../cau-hinh-chung/contract/.../01-openapi.json`; bản mô tả trong `../bao-cao/docs/02-kien-truc-microservices-va-rest-api.md`.

Payment gọi Notification bằng `X-Internal-Key`; frontend không thấy khóa này. Dữ liệu mỗi service nằm trong database riêng. Payment kiểm tra lại số dư và trạng thái học phí khi xác nhận OTP; trừ tiền, gạch nợ, đánh dấu giao dịch và OTP trong một commit. Email xác nhận được gửi sau commit; job `PENDING` được thử lại định kỳ khi SMTP lỗi.

## Kiểm thử

Tại thư mục `src`:

```powershell
python -m pytest tests -q
cd frontend
npm run build
```

`tests/test_payment.py` kiểm tra OTP sai/hết hạn, thanh toán thành công, gửi email, idempotency, hai giao dịch đồng thời trên cùng ví và hai ví cùng trả một khoản. Test dùng SQLite để tạo database riêng từng ca; bản Docker tích hợp dùng PostgreSQL. Kiểm thử thực tế SMTP dùng Mailpit. Sau khi chạy giao dịch demo, dữ liệu được lưu bền; muốn bắt đầu lại từ seed mẫu, dừng Compose và **chỉ khi muốn xóa dữ liệu demo** mới xóa volume của stack.

Khi stack Docker đang chạy, `python tests/integration_postgres.py` kiểm tra T21/T22 trực tiếp trên PostgreSQL bằng các bản ghi thử riêng rồi tự dọn chúng. Script đọc `POSTGRES_PASSWORD` và `JWT_SECRET` từ `src/.env` nếu có.

## Giới hạn

Ứng dụng là mô phỏng học phần, không kết nối ngân hàng hoặc hệ thống công nợ thật của TDTU. Payment Service hiện dùng `Base.metadata.create_all()` và seed idempotent; khi triển khai lâu dài cần thêm migration có phiên bản cho Payment DB. Sơ đồ, báo cáo và mã nguồn phải được cập nhật cùng nhau nếu hợp đồng API của nhóm đổi.
