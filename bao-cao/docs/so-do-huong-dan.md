# Bộ sơ đồ draw.io iBanking

Mở `ibanking-so-do-day-du.drawio` bằng diagrams.net/draw.io để xem 5 trang. Các file `01` đến `05` là bản riêng từng trang, tiện chèn vào báo cáo hoặc slide.

1. `01-use-case.drawio`: người nộp tiền, email provider và sáu use case chính.
2. `02-microservices-architecture.drawio`: React UI, Account, Payment, Notification, database theo quyền sở hữu và SMTP.
3. `03-erd.drawio`: entity, thuộc tính, khóa và quan hệ. `users` và `email_messages` lấy từ migration A; các bảng Payment là thiết kế logic theo hợp đồng 1.0.0, cần đối chiếu migration B khi nhận source.
4. `04-payment-otp-flow.drawio`: tra cứu, tạo payment, OTP 5 phút, xác nhận và cập nhật tài chính nguyên tử.
5. `05-concurrency.drawio`: hai tình huống bắt buộc T21 và T22.

Nguồn đối chiếu: đề dự án, rubric, `cauhinhchung.zip`, migration Account/Notification và source frontend phần A. File `.drawio` là nguồn chỉnh sửa; ảnh trong `previews/` chỉ là ảnh xem trước từ tọa độ XML vì môi trường hiện không có draw.io desktop exporter.

Trước khi nộp báo cáo cuối, B cần xác nhận ERD Payment khớp bảng và constraint đã hiện thực. Cập nhật sơ đồ kiến trúc và luồng nếu API hoặc cách gửi email thay đổi khi ghép hệ thống.
