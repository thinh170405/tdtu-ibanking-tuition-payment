# Nội dung slide phần A

## Slide 1 — Bài toán và phạm vi

- Phân hệ thanh toán học phí trên iBanking.
- Người nộp đăng nhập, tra cứu MSSV, thanh toán toàn bộ, xác nhận OTP và xem lịch sử.
- A phụ trách Account, Notification, frontend và tích hợp giao diện.

## Slide 2 — Use Case

- Chèn sơ đồ từ `use-case-A.puml`.
- Actor: người nộp, hệ thống email.
- Luồng chính và các nhánh lỗi: MSSV sai, đã đóng, thiếu tiền, OTP sai/hết hạn.

## Slide 3 — Kiến trúc microservices

- Chèn sơ đồ từ `architecture.md`.
- Account sở hữu danh tính; Payment sở hữu tài chính và OTP; Notification sở hữu trạng thái email.
- UI gọi Account và Payment; Payment gọi Notification bằng khóa nội bộ.

## Slide 4 — Account Service

- Argon2 password hash, JWT HS256 1 giờ; kiểm tra chữ ký, issuer, audience, hạn dùng.
- API login/profile, request validation và mã lỗi.
- Seed u1/u2 thống nhất ID với Payment.

## Slide 5 — Notification Service

- Hai mẫu: OTP và xác nhận thanh toán.
- `messageId` + payload hash: cùng nội dung đã gửi trả 200; khác nội dung 409.
- Gửi lỗi trả 503 và cho retry; dùng SMTP thật khi tích hợp.

## Slide 6 — Giao diện và tích hợp

- Ảnh đăng nhập, hồ sơ/số dư, tra cứu, OTP, kết quả/lịch sử (chụp sau khi chạy).
- Tự tra cứu MSSV đủ 8 chữ số; hủy response cũ; người nộp chỉ đọc.
- Sau confirm đọc lại wallet và lịch sử từ Payment.

## Slide 7 — Kiểm thử và demo

- Hiện tại: 3 test phần A pass, frontend build pass, migration/seed pass.
- Payment mock chỉ dùng phát triển UI; OTP mock 123456.
- Sau ghép: demo email thật và toàn luồng; A chạy lại hai bài concurrency của B.

## Slide 8 — Đóng góp và giới hạn

- A: Account, Notification, frontend, Use Case, sơ đồ kiến trúc, test và tài liệu phần A.
- Chưa có kết quả chạy Compose container và email đến inbox tại thời điểm viết; bổ sung bằng chứng sau khi cấu hình môi trường và ghép B.
