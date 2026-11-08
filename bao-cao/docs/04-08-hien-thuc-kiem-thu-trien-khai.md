# 4. Cơ sở dữ liệu và lưu trữ

## 4.1. Mô hình dữ liệu triển khai

Sơ đồ [Physical ERD](./04-physical-erd-final.drawio) mô tả tám bảng triển khai. Hệ thống có ba database PostgreSQL độc lập. Account DB chứa bảng `users` với khóa chính `id`, `username` duy nhất, `password_hash`, `full_name`, `phone`, `email`. Notification DB chứa `email_messages` với `message_id` làm khóa chính, `payload_hash`, `status`, `updated_at`. Payment DB chứa `wallets`, `students`, `tuitions`, `payments`, `otps` và `email_jobs`. `user_id` ở Payment là tham chiếu logic tới Account; không tạo foreign key xuyên database.

Trong Payment DB, `wallets.balance >= 0`, `tuitions.amount > 0`, `(payments.user_id, payments.request_id)` duy nhất, mỗi payment có tối đa một bản ghi OTP và một email job xác nhận. Bảng `payments` giữ số tiền được chốt ở lúc tạo giao dịch, trạng thái và các mốc thời gian để phục vụ lịch sử. OTP chỉ lưu hash, thời điểm phát hành, hết hạn và thời điểm sử dụng. Học phí được đánh dấu `PAID` trong cùng transaction với trừ số dư và cập nhật payment `SUCCESS`.

Account và Notification dùng migration SQL theo phiên bản. Payment hiện tạo schema từ SQLAlchemy model và seed dữ liệu mẫu theo hướng idempotent; cần bổ sung migration theo phiên bản trước khi áp dụng cho môi trường vận hành lâu dài. Dữ liệu mẫu lấy từ hợp đồng chung `02-du-lieu-mau.json` và phần mở rộng `src/data/demo-extra.json`. Bộ seed hiện có năm tài khoản, 24 sinh viên, 22 khoản học phí và các giao dịch mẫu cho ca thành công, đã thanh toán, thiếu số dư và số dư bằng đúng số tiền. Seed bổ sung không ghi đè giao dịch hoặc số dư hiện có.

## 4.2. Tính nhất quán dữ liệu

Khi xác nhận OTP, Payment mở database transaction, khóa giao dịch, ví và khoản học phí liên quan, kiểm tra lại OTP, số dư và trạng thái khoản học phí. Sau đó hệ thống trừ số dư, gạch nợ, đánh dấu giao dịch thành công, đánh dấu OTP đã dùng và thêm email job; các bước này được commit cùng nhau. Lỗi trước commit làm rollback. Cùng giao dịch đã `SUCCESS` được trả lại kết quả cũ khi xác nhận lặp, không trừ tiền thêm. Khi gửi email xác nhận lỗi sau commit, job còn `PENDING` để thử lại định kỳ; trạng thái tài chính vẫn `SUCCESS`.

# 5. Hiện thực service và luồng thanh toán

## 5.1. Account Service

Account Service được viết bằng FastAPI và SQLAlchemy. Mật khẩu được kiểm tra qua Argon2; JWT ký bằng HS256, mang `sub`, email, issuer, audience, thời điểm phát hành và hết hạn. API hồ sơ kiểm tra token và đối chiếu tài khoản trước khi trả họ tên, điện thoại, email. Password hash không xuất hiện trong response. CORS chỉ cho phép origin của frontend được cấu hình.

## 5.2. Payment Service

Sơ đồ [Payment and OTP Flow](./05-payment-otp-flow-final.drawio) thể hiện luồng thành công và lỗi. Payment Service thật cung cấp toàn bộ API ví, tra cứu học phí, tạo giao dịch, lịch sử và xác nhận OTP. Tạo payment chỉ cho phép thanh toán toàn bộ số tiền từ Tuition; `requestId` UUID giúp xử lý yêu cầu lặp. OTP gồm sáu chữ số, gắn đúng payment, có thời hạn năm phút, được băm trước khi lưu và gửi qua Notification. Khi xác nhận, service kiểm tra lại điều kiện để chống thay đổi số dư/học phí trong lúc chờ OTP. Hai loại tranh chấp được xử lý ở server: nhiều payment cùng ví và nhiều ví cùng trả một khoản.

## 5.3. Notification Service

Notification nhận `POST /internal/v1/notifications/email` từ Payment với `X-Internal-Key`. Hai loại thư là `OTP` và `PAYMENT_SUCCESS`. `messageId` và hash payload giúp cùng nội dung gửi lặp trả `SENT` mà không gửi thêm, còn trùng ID nhưng đổi nội dung trả lỗi 409. SMTP được cấu hình qua biến môi trường. Trong stack Docker demo, Mailpit nhận thư vào hộp thử tại cổng 8025; không có email ra Internet.

## 5.4. Frontend

Giao diện React thực hiện đăng nhập, hiển thị hồ sơ và số dư ở chế độ chỉ đọc, tự tra cứu khi MSSV đủ tám chữ số, chấp nhận điều khoản, tạo giao dịch, nhập OTP, hiển thị kết quả và lịch sử. Request tra cứu cũ bị hủy, đồng thời số thứ tự request ngăn phản hồi chậm ghi đè MSSV mới. Sau thanh toán, frontend đọc lại số dư và lịch sử từ backend, không tự tính số dư.

# 6. Transaction và xử lý đồng thời

Sơ đồ [Concurrency and Consistency](./06-concurrency-final.drawio) minh họa T21 và T22 trên PostgreSQL.

**Trường hợp T21:** Một ví có 10 triệu đồng tạo hai giao dịch thanh toán hai khoản học phí, mỗi khoản 7 triệu. Hai yêu cầu xác nhận chạy đồng thời; chỉ một giao dịch được `SUCCESS`, số dư cuối là 3 triệu và khoản còn lại chưa được thanh toán. Kiểm thử tự động đã xác nhận kết quả này trên SQLite và PostgreSQL của stack Docker.

**Trường hợp T22:** Hai ví cùng tạo giao dịch cho một khoản học phí. Khi xác nhận đồng thời, chỉ một giao dịch được `SUCCESS`; ví thắng bị trừ 7 triệu, ví còn lại không bị trừ. Kiểm thử tự động đã xác nhận kết quả này trên SQLite và PostgreSQL. Stack PostgreSQL dùng khóa dòng `SELECT FOR UPDATE`; các phép đo tải lớn và độ trễ chưa được thực hiện.

Idempotency có hai lớp: cặp `(user_id, request_id)` chống tạo trùng payment; gọi confirm lại payment đã thành công trả kết quả cũ. Notification dùng `messageId` cố định để tránh gửi trùng khi Payment thử lại. Các thao tác tài chính nằm trong Payment DB để có thể commit nguyên tử, thay vì giao dịch phân tán xuyên ba service.

# 7. Kiểm thử, triển khai và trình diễn

## 7.1. Kiểm thử đã thực hiện

| Hoạt động | Kết quả quan sát | Phạm vi kết luận |
|---|---|---|
| `python -m pytest tests -q` | 6 bài kiểm thử đạt | Account, Notification, Payment; gồm OTP sai/hết hạn, hai ca đồng thời trên SQLite. |
| `npm run build` | Build thành công | Mã Frontend biên dịch được. |
| `docker compose -f compose.yaml config --quiet` | Không báo lỗi | Cú pháp cấu hình Compose hợp lệ. |
| `docker compose -f compose.yaml up --build -d` | Sáu container chạy | PostgreSQL, Mailpit, Account, Payment, Notification, Frontend. |
| Luồng tích hợp trên Docker | Login 200; tạo payment 201; confirm OTP 200 `SUCCESS`; ví từ 10 triệu về 0; khoản HP005 thành `PAID`; Mailpit có OTP và thư xác nhận | Chứng minh luồng thực với Payment Service, PostgreSQL và SMTP thử nội bộ. Không chứng minh gửi ra hộp thư Internet. |
| T21/T22 trên PostgreSQL | Cả hai ca đạt bằng `tests/integration_postgres.py` | Test dùng bản ghi thử riêng và tự dọn sau chạy; chưa đo tải lớn. |

`src/tests/test_account_notification.py` kiểm tra Account và Notification; `src/tests/test_payment.py` kiểm tra Payment và tranh chấp trên SQLite; `src/tests/integration_postgres.py` kiểm tra T21/T22 trên PostgreSQL và Mailpit. Kết quả được ghi ngày 08/11/2026. Sau kiểm thử, HP005 được khôi phục về trạng thái ban đầu.

## 7.2. Hướng dẫn chạy và demo

Tại thư mục `src`, chạy `docker compose -f compose.yaml up --build -d`. Mở `http://localhost:5173` để dùng ứng dụng và `http://localhost:8025` để xem email thử. Dùng tài khoản mẫu `demo1` và mật khẩu `Demo!2026`, tra cứu MSSV chưa đóng, đồng ý điều khoản, tạo giao dịch, đọc OTP trong Mailpit rồi xác nhận. Kiểm tra lại số dư, trạng thái học phí, lịch sử và thư xác nhận. API docs của từng service ở `/docs` trên các cổng 8081, 8082 và 8083. Hướng dẫn chi tiết và giới hạn demo nằm trong `src/README.md`.

## 7.3. Giới hạn nghiệm thu

Đây là mô phỏng học phần, không kết nối tài khoản ngân hàng hoặc hệ thống công nợ thật TDTU. Mailpit chỉ là hộp thư thử. Hai ca đồng thời đã có kiểm thử tự động trên SQLite và PostgreSQL; cần thêm kiểm thử tải lớn để đo độ trễ dưới tải. Payment DB hiện chưa có migration phiên bản.

# 8. Kết luận

Dự án hiện có ba service với database riêng, Frontend tích hợp API, OTP email qua Mailpit, giao dịch tài chính lưu bền và báo cáo thiết kế. Luồng thanh toán thật đã chạy qua Docker, từ đăng nhập đến thư xác nhận; hai ca đồng thời đã đạt trên PostgreSQL. Bước nâng cấp tiếp theo trước môi trường vận hành là migration Payment DB, kiểm thử tải lớn, cấu hình SMTP/TLS thật, quản lý bí mật và ghi log/tracing phù hợp.

**Tài liệu đối chiếu:** Đề bài phân hệ đóng học phí iBanking TDTU; rubric giữa kỳ; hợp đồng OpenAPI và dữ liệu mẫu trong `cau-hinh-chung/contract`; mã nguồn và README trong `src/`.
