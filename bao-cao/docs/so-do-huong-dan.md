# Bộ sơ đồ draw.io iBanking

Mở [bộ sơ đồ đầy đủ](./ibanking-so-do-day-du.drawio) bằng diagrams.net hoặc draw.io. File này có sáu trang, toàn bộ nhãn trên sơ đồ bằng tiếng Anh và có thể chỉnh sửa trực tiếp. Mỗi trang cũng có file riêng:

1. [Use Case Diagram](./01-use-case.drawio): khách hàng, nhà cung cấp email, sáu use case và ranh giới phân hệ.
2. [Microservices Architecture](./02-microservices-architecture.drawio): Frontend, Account, Payment, Notification, ba database logic trong PostgreSQL và SMTP Mailpit.
3. [Conceptual ERD](./03-conceptual-erd.drawio): năm thực thể nghiệp vụ theo đề bài.
4. [Physical ERD](./04-physical-erd.drawio): tám bảng đang được hiện thực; nét đứt là liên kết logic xuyên database.
5. [Payment and OTP Flow](./05-payment-otp-flow.drawio): từ tra cứu tới OTP, transaction và gửi biên nhận.
6. [Concurrency and Consistency](./06-concurrency.drawio): hai trường hợp T21 và T22 đã được kiểm thử.

Nguồn đối chiếu: `src/compose.yaml`, mã nguồn ba service, migration và `src/tests/integration_postgres.py`. Chạy `python bao-cao/tools/build_project_diagrams.py` từ gốc dự án để dựng lại các file `.drawio`. Chạy `python bao-cao/tools/preview_drawio.py bao-cao/docs/ibanking-so-do-day-du.drawio` để tạo ảnh xem nhanh trong `previews/`. Ảnh này dùng bộ vẽ hình học gần đúng; khi xuất ảnh để nộp, mở file `.drawio` trong diagrams.net và dùng chức năng Export của ứng dụng.
