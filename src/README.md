# Phân hệ đóng học phí iBanking

## Chạy toàn bộ hệ thống

Yêu cầu Docker Desktop. Tại thư mục `src`, chạy:

```powershell
docker compose -f compose.yaml up --build -d
docker compose -f compose.yaml ps
```

Mở giao diện tại http://localhost:5173. Đăng nhập `demo3` / `Demo!2026` để thử dữ liệu mới. Account, Payment, Notification lần lượt ở cổng 8081, 8082, 8083; PostgreSQL host 5433. Khi dùng cấu hình mặc định, OTP và email xác nhận nằm trong Mailpit tại http://localhost:8025.

### Xem dữ liệu bằng pgAdmin

Mở http://localhost:5050 và đăng nhập bằng `PGADMIN_EMAIL` / `PGADMIN_PASSWORD` trong `src/.env` (nếu chưa đặt: `admin@ibanking-demo.org` / `local-demo-pgadmin`). Trong pgAdmin, chọn **Add New Server**:

- **General → Name:** `iBanking local`
- **Connection → Host name/address:** `postgres` (tên service Docker, không phải `localhost`)
- **Connection → Port:** `5432`
- **Connection → Maintenance database:** `postgres`
- **Connection → Username:** `ibanking`
- **Connection → Password:** giá trị `POSTGRES_PASSWORD` trong `src/.env` (nếu chưa đặt: `local-demo-password`)

Sau khi lưu, mở **Databases → ibanking_account / ibanking_payment / ibanking_notification → Schemas → public → Tables**. Dữ liệu PostgreSQL nằm trong volume `full_db`; cấu hình pgAdmin nằm trong volume `pgadmin_data`.

File `compose.yaml` dùng mật khẩu và khóa **chỉ cho môi trường demo local**. Khi triển khai ngoài máy cá nhân, đặt `POSTGRES_PASSWORD`, `JWT_SECRET`, `INTERNAL_API_KEY` riêng trong `.env` và dùng HTTPS. Mặc định SMTP dùng Mailpit; nếu cấu hình `SMTP_HOST`, `SMTP_PORT`, `SMTP_SECURITY`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM` trong `.env`, Notification sẽ gửi qua máy chủ SMTP đó.

## Luồng sử dụng

Sau đăng nhập, trang `/` hiển thị tổng quan tài khoản. Chọn **Đóng học phí** để mở trang `/tuition-payment`.

1. Tra cứu MSSV 8 chữ số và xem khoản học phí.
2. Đồng ý điều khoản, chọn thanh toán toàn bộ.
3. Bảng nhập OTP mở sau khi tạo giao dịch; nhập mã trong vòng 5 phút theo đồng hồ đếm ngược. Nếu không nhận được email, có thể gửi lại sau 30 giây; mã cũ sẽ hết hiệu lực.
4. Kiểm tra kết quả, số dư, học phí, lịch sử và email xác nhận.

### Dữ liệu mẫu

`data/demo-base.json` chứa dữ liệu mẫu gốc; `data/demo-extra.json` thêm `demo3` (20 triệu), `demo4` (3 triệu), `demo5` (15 triệu) với mật khẩu `Demo!2026`. Đây là số dư ban đầu; giao dịch đã thực hiện sẽ làm thay đổi số dư. Nếu không đặt `DEMO_EMAIL_3/4/5`, OTP của các tài khoản này được gửi tới `DEMO_EMAIL_1`.

| MSSV | Số tiền | Tình huống mẫu |
|---|---:|---|
| `52600007` | 3.200.000 VND | Chưa đóng; `demo3` đủ tiền, `demo4` thiếu tiền. |
| `52600010` | 1.250.000 VND | Khoản nhỏ, có thể đóng bằng `demo4`. |
| `52600011` | 8.000.000 VND | Đã đóng; có lịch sử mẫu của `demo3`. |
| `52600012` | 12.000.000 VND | Chưa đóng; `demo3` đủ tiền. |
| `52600017` | 3.000.000 VND | Đã đóng; có lịch sử mẫu của `demo5`. |
| `52600019` | 18.000.000 VND | Khoản lớn, chỉ `demo3` đủ tiền lúc mới seed. |
| `52600020` | 600.000 VND | Khoản nhỏ nhất trong bộ mẫu mới. |
| `52600024` | — | Sinh viên tồn tại nhưng chưa có khoản học phí. |

Còn nhiều khoản `52600008`–`52600023` với số tiền từ 600.000 đến 18 triệu. MSSV `52699999` không tồn tại. Chạy lại seed không đặt lại số dư hoặc giao dịch đã phát sinh.

## Cấu trúc và API

- `services/account`: `users`, đăng nhập và hồ sơ; phát JWT.
- `services/payment`: `wallets`, `students`, `tuitions`, `payments`, `otps`, `email_jobs`; kiểm tra OTP, thanh toán và xử lý đồng thời trong database transaction.
- `services/notification`: `email_messages`, gửi và chống gửi trùng qua SMTP.
- `frontend`: React; gọi Account và Payment bằng Bearer JWT.
- API đang chạy được mô tả tại `/docs` của từng backend; bản thiết kế nằm trong `../bao-cao/docs/02-kien-truc-microservices-va-rest-api.md`.

Payment gọi Notification bằng `X-Internal-Key`; frontend không thấy khóa này. Dữ liệu mỗi service nằm trong database riêng. Payment kiểm tra lại số dư và trạng thái học phí khi xác nhận OTP; trừ tiền, gạch nợ, đánh dấu giao dịch và OTP trong một commit. Email xác nhận được gửi sau commit; job `PENDING` được thử lại định kỳ khi SMTP lỗi.

## Kiểm thử

Tại thư mục `src`:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
cd frontend
npm run build
```

`tests/test_payment.py` kiểm tra OTP sai/hết hạn, thanh toán thành công, gửi email, idempotency và giao dịch đồng thời. Test dùng SQLite riêng từng ca; Docker dùng PostgreSQL. Sau khi chạy giao dịch demo, dữ liệu được lưu bền; chỉ xóa volume khi muốn đặt lại toàn bộ dữ liệu.

Khi stack Docker đang chạy, `python tests/integration_postgres.py` kiểm tra T21/T22 trực tiếp trên PostgreSQL bằng các bản ghi thử riêng rồi tự dọn chúng. Script đọc `POSTGRES_PASSWORD` và `JWT_SECRET` từ `src/.env` nếu có.

## Giới hạn

Ứng dụng là mô phỏng học phần, không kết nối ngân hàng hoặc hệ thống công nợ thật của TDTU. Payment Service hiện dùng `Base.metadata.create_all()` và seed idempotent; khi triển khai lâu dài cần thêm migration có phiên bản cho Payment DB. Sơ đồ, báo cáo và mã nguồn phải được cập nhật cùng nhau nếu hợp đồng API của nhóm đổi.
