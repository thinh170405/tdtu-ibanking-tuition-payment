# Hướng dẫn đọc cấu trúc và mã nguồn iBanking

Tài liệu này giải thích **bản mã nguồn hiện tại** của phân hệ đóng học phí, tách riêng khỏi báo cáo giữa kỳ. Nếu muốn chạy chương trình ngay, xem [hướng dẫn chạy](src/README.md). Nếu muốn đối chiếu nghiệp vụ và sơ đồ, xem [báo cáo](bao-cao/docs/01-phan-tich-nghiep-vu-uml.md) và [bộ sơ đồ draw.io](bao-cao/docs/ibanking-diagrams-final.drawio).

## 1. Nhìn tổng thể

Người dùng mở giao diện React, đăng nhập ở Account Service rồi dùng JWT để gọi Account và Payment Service. Payment quản lý ví, sinh viên, học phí, giao dịch và OTP. Khi cần gửi OTP hoặc biên nhận, Payment gọi Notification Service qua REST nội bộ. Notification gửi SMTP đến Mailpit trong cấu hình demo. Ba service dùng **ba database logic riêng** trong **một PostgreSQL instance** của Docker Compose.

```text
Browser / React (:5173)
  ├─ HTTP + Bearer JWT ──> Account (:8081) ──> ibanking_account / users
  └─ HTTP + Bearer JWT ──> Payment (:8082) ──> ibanking_payment
                                      │          wallets, students, tuitions,
                                      │          payments, otps, email_jobs
                                      └─ HTTP + X-Internal-Key ──> Notification (:8083)
                                                                  ├─ ibanking_notification / email_messages
                                                                  └─ SMTP ──> Mailpit (:8025 UI)
```

Các cổng và lời gọi HTTP trên là cấu hình **local demo** trong [compose.yaml](src/compose.yaml). Không xem đây là cấu hình HTTPS/TLS cho môi trường thực tế.

## 2. Cấu trúc thư mục: đọc file nào để hiểu việc gì?

| Đường dẫn | Nội dung cần đọc |
|---|---|
| [README.md](README.md) | Đề bài và các tiêu chí bàn giao. |
| [src/README.md](src/README.md) | Cách chạy Docker, tài khoản và tình huống dữ liệu mẫu, cách kiểm thử. |
| [src/compose.yaml](src/compose.yaml) | Sáu container: PostgreSQL, Mailpit, Account, Payment, Notification, Frontend; cổng, biến môi trường và thứ tự khởi động. |
| [src/docker/postgres-init.sql](src/docker/postgres-init.sql) | Tạo ba database logic khi volume PostgreSQL được khởi tạo lần đầu. |
| [src/Dockerfile.service](src/Dockerfile.service) | Image Python dùng chung cho ba backend; cài dependency và chép mã nguồn, dữ liệu, hợp đồng API. |
| [src/services/common.py](src/services/common.py) | Kiểu request không nhận trường thừa; chuẩn lỗi `{code, message}`; lỗi validation HTTP 400 và lỗi hệ thống HTTP 500. |
| [src/services/account/app.py](src/services/account/app.py) | Bảng `users`, xác thực username/password, phát và kiểm tra JWT, trả hồ sơ người dùng. |
| [src/services/payment/app.py](src/services/payment/app.py) | Sáu bảng của Payment, API ví/học phí/giao dịch, OTP, khóa dữ liệu khi xác nhận, gửi và thử lại email biên nhận. |
| [src/services/notification/app.py](src/services/notification/app.py) | API gửi email nội bộ, kiểm tra `X-Internal-Key`, chống xử lý trùng bằng `messageId`, gửi SMTP. |
| [src/services/migrate.py](src/services/migrate.py) | Chạy các file SQL migration có phiên bản cho Account và Notification. |
| [src/services/account/seed.py](src/services/account/seed.py), [src/services/payment/seed.py](src/services/payment/seed.py) | Nạp dữ liệu demo nếu bản ghi chưa có; Account cập nhật email demo đã cấu hình. Payment tạo bảng bằng SQLAlchemy `create_all`. |
| [src/services/notification/init_db.py](src/services/notification/init_db.py) | Gọi migration của Notification khi container khởi động. |
| [src/frontend/src/main.jsx](src/frontend/src/main.jsx) | Toàn bộ logic giao diện React: đăng nhập, tổng quan, trang thanh toán, gọi API và hiển thị lịch sử. |
| [src/frontend/src/style.css](src/frontend/src/style.css) | Bố cục và kiểu hiển thị giao diện. |
| [src/frontend/package.json](src/frontend/package.json), [src/frontend/Dockerfile](src/frontend/Dockerfile) | Lệnh Vite, dependency frontend và cách dựng container. |
| [src/data/demo-extra.json](src/data/demo-extra.json) | Tài khoản, ví, học phí và giao dịch mẫu bổ sung. |
| [cau-hinh-chung/contract](cau-hinh-chung/contract/) | Hợp đồng OpenAPI, dữ liệu mẫu gốc và ma trận kiểm thử. |
| [src/tests](src/tests/) | Unit test và kiểm thử tích hợp trên PostgreSQL. |

## 3. Trách nhiệm và quyền sở hữu dữ liệu

| Thành phần | Trách nhiệm | Dữ liệu sở hữu |
|---|---|---|
| Account Service | Kiểm tra mật khẩu Argon2, phát JWT HS256, trả hồ sơ tài khoản. | `ibanking_account.users`. |
| Payment Service | Tra ví/học phí; tạo giao dịch chờ OTP; xác nhận OTP; trừ ví, gạch nợ và lưu lịch sử; quản lý job email xác nhận. | `ibanking_payment.wallets`, `students`, `tuitions`, `payments`, `otps`, `email_jobs`. |
| Notification Service | Nhận yêu cầu gửi OTP/biên nhận từ Payment, kiểm tra khóa nội bộ, gửi SMTP và lưu trạng thái thông điệp. | `ibanking_notification.email_messages`. |
| Frontend | Hiển thị dữ liệu và trạng thái, thu thập MSSV/điều khoản/OTP, gọi API. | Không sở hữu bảng dữ liệu; JWT đang lưu trong `sessionStorage`. |

`wallets.user_id` và `payments.user_id` tham chiếu **logic** đến `users.id`: chúng ở database khác nên không có khóa ngoại vật lý nối sang Account. `email_jobs` liên hệ `email_messages` qua `messageId` trong lời gọi API, không có FK xuyên service. Hai bảng `schema_migrations` do bộ chạy migration tạo ra để ghi phiên bản SQL đã áp dụng; không phải bảng nghiệp vụ.

## 4. Khởi động và dữ liệu mẫu

Từ thư mục `src`:

```powershell
docker compose -f compose.yaml up --build -d
docker compose -f compose.yaml ps
```

PostgreSQL tạo ba database qua `postgres-init.sql` lúc volume mới được tạo. Container Account chạy `account.seed` trước Uvicorn; thao tác này áp dụng migration `001_users.sql` rồi nạp tài khoản. Notification chạy `notification.init_db`, áp dụng migration `001_messages.sql`. Payment chạy `payment.seed`, tạo các bảng từ model SQLAlchemy rồi nạp dữ liệu từ hợp đồng chung và `src/data/demo-extra.json`. Các seed kiểm tra bản ghi đã có, vì vậy chạy lại container **không đặt lại số dư hoặc lịch sử**.

Mở giao diện tại `http://localhost:5173`, Mailpit tại `http://localhost:8025`. Tài khoản thử và các MSSV mẫu có trong [src/README.md](src/README.md). Cấu hình demo mặc định dùng SMTP tới Mailpit; Notification cũng hỗ trợ biến môi trường SMTP khác trong [compose.yaml](src/compose.yaml).

## 5. Các API đang chạy

Phần lớn API nằm dưới `/api/v1`. Ngoài các API sau, mỗi backend có `GET /api/v1/health`.

| Service | Method và URI | Tác dụng |
|---|---|---|
| Account | `POST /api/v1/auth/login` | Nhận `username`, `password`; trả `accessToken`, `tokenType`, `expiresIn`. |
| Account | `GET /api/v1/users/me` | Đọc Bearer JWT; trả `userId`, `fullName`, `phone`, `email`. |
| Payment | `GET /api/v1/wallet` | Trả ví và số dư của người đang đăng nhập. |
| Payment | `GET /api/v1/tuition/{mssv}` | Tra MSSV 8 chữ số; trả sinh viên, khoản học phí và trạng thái. |
| Payment | `POST /api/v1/payments` | Nhận `tuitionId`, `termsAccepted`, `requestId` (UUID); tạo `PENDING_OTP` và gửi OTP. Thành công trả HTTP 201. |
| Payment | `GET /api/v1/payments` | Trả lịch sử giao dịch của người dùng, sắp theo thời gian tạo giảm dần. |
| Payment | `GET /api/v1/payments/{payment_id}` | Trả một giao dịch nếu thuộc người dùng hiện tại. |
| Payment | `POST /api/v1/payments/{payment_id}/confirm` | Nhận OTP 6 chữ số; xác nhận và hoàn tất thanh toán. |
| Notification | `POST /internal/v1/notifications/email` | Payment gọi với `X-Internal-Key`; nhận yêu cầu loại `OTP` hoặc `PAYMENT_SUCCESS`. |

Frontend gọi Account/Payment trực tiếp bằng `Authorization: Bearer <JWT>`. Account phát JWT với `sub` là user ID, `email`, `iss`, `aud`, `iat`, `exp`; Payment kiểm tra chữ ký và các claim cần thiết. Payment gọi Notification bằng `X-Internal-Key`, không gửi khóa này xuống trình duyệt. Lỗi trả JSON dạng `{"code":"...","message":"..."}`; mã HTTP được dùng thực tế gồm 400, 401, 403, 404, 409, 422, 500 và 503 tùy tình huống.

## 6. Theo một giao dịch từ đầu đến cuối

1. **Đăng nhập:** [Account `login`](src/services/account/app.py) tra `users`, kiểm tra password hash và phát JWT. Frontend lưu token trong `sessionStorage`, sau đó gọi hồ sơ, ví và lịch sử.
2. **Tra cứu:** Khi MSSV đủ 8 chữ số, frontend gọi Payment `GET /tuition/{mssv}`. Payment trả khoản học phí gắn với sinh viên; frontend chỉ hiển thị thông tin người nộp lấy từ hồ sơ đăng nhập.
3. **Tạo giao dịch:** Frontend yêu cầu đồng ý điều khoản và tạo `requestId` UUID. Payment kiểm tra ví tồn tại, học phí chưa đóng và đủ số dư; lưu `payments.status=PENDING_OTP` cùng bản ghi `otps` chỉ chứa hash và thời hạn **5 phút**. Sau khi commit, Payment nhờ Notification gửi OTP đến email trong JWT. Chưa trừ ví ở bước này.
4. **Xác nhận OTP:** Payment kiểm tra giao dịch thuộc người dùng, còn `PENDING_OTP`, OTP chưa dùng, chưa hết hạn và đúng hash. Sau đó khóa hàng ví và học phí, **kiểm tra lại** trạng thái và số dư. Trong một database transaction, Payment trừ ví, đặt học phí `PAID`, giao dịch `SUCCESS`, đánh dấu OTP đã dùng và thêm `email_jobs` với trạng thái `PENDING`.
5. **Gửi biên nhận:** Sau commit tài chính, Payment gọi Notification để gửi email xác nhận. Nếu chưa gửi được, job vẫn `PENDING`; worker thử lại định kỳ khoảng 30 giây. Lỗi email biên nhận không hoàn tác giao dịch tài chính đã thành công.
6. **Hiển thị kết quả:** Frontend làm mới hồ sơ, ví, lịch sử; lịch sử dùng `paidAt` cho giao dịch thành công và `createdAt` cho các trạng thái khác, định dạng theo múi giờ Việt Nam.

`requestId` dùng để tránh tạo lặp một yêu cầu thanh toán của cùng người dùng. `messageId` dùng ở Notification để nhận biết lần gửi lặp: `otp:<paymentId>` cho OTP và `success:<paymentId>` cho biên nhận. Hai mã phục vụ hai mục đích khác nhau.

### Các nhánh lỗi nên đọc trong code

- MSSV sai định dạng, sinh viên hoặc khoản học phí không tồn tại: xem `tuition()` trong [Payment app](src/services/payment/app.py).
- Chưa đồng ý điều khoản, học phí đã đóng, thiếu số dư, `requestId` bị dùng cho khoản khác: xem `create()`.
- Gửi OTP thất bại: `create()` đánh dấu giao dịch `FAILED`, trả `NOTIFICATION_UNAVAILABLE`; tiền chưa bị trừ.
- OTP sai, đã dùng hoặc hết hạn: xem `confirm()`; OTP sai không trừ tiền, hết hạn đặt giao dịch `EXPIRED`.
- Có giao dịch khác vừa dùng ví hoặc vừa trả cùng khoản học phí: `confirm()` kiểm tra lại **sau khi lấy khóa** và trả `INSUFFICIENT_BALANCE` hoặc `TUITION_ALREADY_PAID`.

## 7. Vì sao thanh toán đồng thời vẫn nhất quán?

Điểm quyết định nằm ở `confirm()`, không phải lần kiểm tra sơ bộ khi tạo giao dịch. Với PostgreSQL, truy vấn `.with_for_update()` khóa hàng giao dịch/OTP rồi hàng ví và học phí. Giao dịch thứ hai phải chờ; khi được chạy tiếp, nó đọc lại số dư hoặc trạng thái học phí đã thay đổi và bị từ chối nếu không còn hợp lệ. Với SQLite ở unit test, code dùng `BEGIN IMMEDIATE` để khóa ghi theo cơ chế SQLite.

Hai ca tích hợp trong [integration_postgres.py](src/tests/integration_postgres.py): **T21** có một ví 10 triệu và hai khoản 7 triệu, chỉ một giao dịch thành công, số dư cuối 3 triệu; **T22** có hai ví cùng trả một khoản 7 triệu, chỉ một giao dịch thành công và ví thua không bị trừ. Các ca này chạy trên PostgreSQL đang mở trong Docker, có tạo và dọn bản ghi thử riêng.

## 8. Đọc giao diện React theo thứ tự

Tất cả logic nằm trong [main.jsx](src/frontend/src/main.jsx), có thể đọc theo nhóm sau:

1. `accountBase`, `paymentBase`, `api()`: cấu hình địa chỉ backend; `api()` gắn Bearer JWT và chuyển lỗi HTTP thành `Error` chứa `code`, `status`.
2. `Dashboard`: trang `/`, hiển thị hồ sơ, số dư, giao dịch gần nhất và nút sang trang đóng học phí.
3. `App` và các `useState`: giữ token, trang hiện tại, hồ sơ, ví, lịch sử, MSSV, học phí, giao dịch, OTP, thông báo.
4. `refresh()`, `login()`, `logout()`: đăng nhập và tải lại dữ liệu. `navigate()` dùng `history.pushState` để chuyển giữa `/` và `/tuition-payment`.
5. `useEffect` theo `mssv`: đợi 300 ms rồi tự tra cứu; `AbortController` và số thứ tự `lookupSeq` ngăn kết quả cũ ghi đè khi người dùng đổi MSSV nhanh.
6. `createPayment()` và `confirm()`: gọi hai API thanh toán; sau xác nhận thành công thì làm mới số dư, học phí và lịch sử.
7. JSX cuối file: ba trạng thái hiển thị chính là form đăng nhập, trang tổng quan và trang đóng học phí. CSS nằm ở [style.css](src/frontend/src/style.css).

Username/password demo đang được điền sẵn trong form để trình diễn. Thông tin người nộp trên trang thanh toán chỉ hiển thị từ `GET /users/me`, không phải ô nhập để người dùng sửa.

## 9. Chạy kiểm thử và đọc kết quả

Từ thư mục `src`, sau khi cài dependency phát triển:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
cd frontend
npm run build
```

[test_account_notification.py](src/tests/test_account_notification.py) kiểm tra đăng nhập, hồ sơ và gửi email nội bộ. [test_payment.py](src/tests/test_payment.py) kiểm tra luồng Payment bằng database thử riêng. Sau khi Docker stack chạy, từ thư mục `src` có thể chạy `python tests/integration_postgres.py` để kiểm tra đồng thời T21/T22 trên PostgreSQL.

## 10. Giới hạn của bản demo

Ứng dụng là mô phỏng học phần, không kết nối ngân hàng hoặc công nợ TDTU thật. Payment hiện tạo bảng bằng `Base.metadata.create_all()` thay vì migration có phiên bản như Account và Notification. Cấu hình Compose mặc định dùng HTTP và khóa/mật khẩu demo local. Nếu thay đổi API hoặc model, cần đối chiếu lại [tài liệu thiết kế REST API](bao-cao/docs/02-kien-truc-microservices-va-rest-api.md) và [sơ đồ](bao-cao/docs/ibanking-diagrams-final.drawio).
