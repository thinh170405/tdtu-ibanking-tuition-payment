# Rà soát gói công việc A

Ngày rà soát: 07/11/2026. Đối chiếu với phân công gói A, hợp đồng 1.0.0 và các file thực tế trong `src/`, `bao-cao/`.

| Mã | Trạng thái | Bằng chứng hiện có | Cần làm để nghiệm thu |
|---|---|---|---|
| A1 | Đạt về nội dung | `A1-phan-tich-nghiep-vu-ibanking.docx`, `docs/01-use-case.drawio`, `docs/use-case-A.puml`; có actor, luồng chính/lỗi và điều kiện trước/sau | Điền tên nhóm và rà lại với API B cuối cùng |
| A2 | Đạt về thiết kế | `docs/02-microservices-architecture.drawio`; có frontend, Account, Payment, Notification, database và SMTP, giao tiếp HTTP/JWT/khóa nội bộ | Đồng bộ sơ đồ với mã Payment B trước khi nộp |
| A3 | Đạt chức năng cơ bản | Migration/seed `users`, Argon2, login/profile, JWT; Account chạy trên PostgreSQL trong Compose, có 2 user và hash Argon2; restart container vẫn truy cập được | Bổ sung test token sai chữ ký, hết hạn, issuer/audience |
| A4 | Đạt một phần | Notification chạy trên PostgreSQL; API thiếu khóa trả 403, SMTP chưa cấu hình trả 503 và lưu FAILED; test với SMTP mô phỏng bao phủ gửi lặp/xung đột/retry | Cấu hình SMTP thật, nhận OTP và email xác nhận vào inbox, lưu ảnh/log |
| A5 | Đạt một phần | React UI có login, hồ sơ/số dư, tự tra cứu MSSV, điều khoản, thanh toán toàn bộ, OTP, kết quả/lịch sử; build thành công | Thử thao tác trực tiếp trong trình duyệt, các lỗi UI và toàn luồng với Payment thật |
| A6 | Đạt một phần | Payment mock, 3 test tự động cho Account/Notification/mock; có OTP sai và thành công | Thêm kịch bản mock delay/lỗi cần cho T37; test UI tự động hoặc bằng chứng thao tác đổi MSSV nhanh |
| A7 | Đạt với Payment mock | `docker compose up --build -d` dựng PostgreSQL, Account, Notification, Payment mock và frontend; cả 4 HTTP endpoint trả 200; API giao dịch mock chạy trọn luồng | Chạy lại từ máy khác/môi trường sạch; khi ghép B cần tắt mock trong demo cuối |
| A8 | Đạt một phần | Word báo cáo A, Word A1, bộ sơ đồ draw.io, bảng API và kết quả test; `slides-A.md` | Ảnh UI/email thật, kết quả tích hợp; tạo slide trình chiếu hoàn chỉnh và cập nhật báo cáo theo code B |

Kết quả bổ sung ngày 07/11/2026: Docker Compose build và chạy đủ 5 container (kể cả PostgreSQL); Account, Notification, Payment mock và frontend đều HTTP 200. Login 200, profile u1, tạo payment 201, OTP sai 422, xác nhận mock 200, số dư mock từ 10 triệu còn 3 triệu; đã restart mock để trả dữ liệu demo về ban đầu. PostgreSQL Account có 2 user và hash Argon2. Notification chưa cấu hình SMTP: khóa thiếu trả 403, gửi với khóa đúng trả 503 và lưu bản ghi FAILED. Kết quả trước đó: `pytest` **3 passed**, `npm run build` **thành công**. Ma trận 37 case vẫn cần điền kết quả từng case; mock không chứng minh transaction của B hay email đến inbox.

**Kết luận:** A1, A2 và A7 với Payment mock có đầu ra đã kiểm tra. A3 chạy trên PostgreSQL; A4–A6 và A8 còn thiếu bằng chứng nghiệm thu cuối theo đúng cột “đầu ra và tiêu chí hoàn thành”.
