# Đề bài giữa kỳ: Phân hệ đóng học phí iBanking

Nguồn: [trang 1](de-bai/1.png), [trang 2](de-bai/2.png), [trang 3](de-bai/3.png). Các mục dưới đây diễn giải yêu cầu của đề để đối chiếu khi thiết kế và nghiệm thu. Hướng dẫn chạy bản hiện thực nằm trong [`src/README.md`](src/README.md).

## Mục tiêu

Xây dựng ứng dụng mô phỏng phân hệ đóng học phí của iBanking. Người dùng dùng số dư khả dụng để thanh toán **toàn bộ** khoản học phí của sinh viên TDTU, cho chính mình hoặc sinh viên khác. Đề không yêu cầu đăng ký tài khoản mới.

## 1. Đăng nhập và thông tin người dùng

**Yêu cầu:** Đăng nhập bằng username và password. Quản lý tối thiểu họ tên, số điện thoại, email, số dư khả dụng và lịch sử giao dịch. Chỉ người đăng nhập thành công mới truy cập chức năng thanh toán học phí.

**Kết quả cần đạt:** Người dùng đăng nhập được và xem đúng thông tin, số dư, lịch sử của mình; người chưa đăng nhập không thực hiện được thanh toán.

## 2. Tra cứu và xác nhận thanh toán học phí

Màn hình thanh toán gồm ba nhóm:

| Nhóm | Dữ liệu và hành vi |
|---|---|
| Người nộp tiền | Họ tên, số điện thoại, email tự lấy từ tài khoản đang đăng nhập và **không cho chỉnh sửa**. |
| Thông tin học phí | Nhập MSSV để hệ thống tự tra cứu, hiển thị họ tên sinh viên và **khoản học phí còn phải thanh toán**. |
| Thông tin thanh toán | Hiển thị số dư khả dụng của người nộp, số tiền cần thanh toán và các thỏa thuận/điều khoản của hệ thống. |

Chỉ cho phép giao dịch khi khoản học phí tồn tại, chưa được thanh toán và số dư khả dụng **lớn hơn hoặc bằng** số tiền cần trả. Không hỗ trợ thanh toán một phần. Nút **Xác nhận giao dịch** chỉ khả dụng khi thông tin cần thiết đầy đủ, hợp lệ.

**Kết quả cần đạt:** Tra cứu MSSV hợp lệ cho đúng sinh viên và số tiền; người dùng không sửa được thông tin người nộp; khoản không tồn tại, đã thanh toán, thiếu dữ liệu hoặc thiếu số dư đều bị chặn.

## 3. Xác thực bằng OTP

Sau khi người dùng xác nhận giao dịch, hệ thống gửi OTP qua **email của người nộp**. Mỗi OTP phải gắn với một giao dịch cụ thể, không trùng với OTP đang có hiệu lực của giao dịch khác, có hạn sử dụng **tối đa 5 phút** và chỉ được dùng thành công **một lần**. Chỉ xử lý tiếp khi OTP người dùng nhập hợp lệ và còn hạn.

**Kết quả cần đạt:** OTP đến đúng email; mã sai, hết hạn, đã dùng hoặc thuộc giao dịch khác không thể hoàn tất thanh toán; mã hợp lệ chỉ xác nhận đúng giao dịch của nó.

## 4. Xử lý giao dịch thành công

Sau khi xác thực OTP, hệ thống phải thực hiện đủ các bước:

1. Kiểm tra lại tính hợp lệ của giao dịch và số dư khả dụng.
2. Trừ số tiền tương ứng khỏi tài khoản người nộp.
3. Cập nhật khoản học phí tương ứng thành **đã thanh toán**.
4. Lưu giao dịch vào lịch sử giao dịch của người dùng.
5. Gửi email xác nhận thành công đến người nộp.
6. Kết thúc giao dịch và hiển thị kết quả cho người dùng.

**Kết quả cần đạt:** Số dư, trạng thái học phí, lịch sử và kết quả hiển thị phản ánh cùng một giao dịch thành công; người nộp nhận email xác nhận.

## 5. Tính nhất quán và xử lý đồng thời

- **Nhiều giao dịch trên cùng tài khoản:** Không cho các giao dịch đồng thời cùng sử dụng một phần số dư dẫn đến chi tiêu vượt số dư khả dụng.
- **Nhiều tài khoản trả cùng khoản học phí:** Nếu hai người cùng trả cho một MSSV, khoản học phí chỉ được thanh toán thành công **một lần**.

**Kết quả cần đạt:** Không có số dư sai, thanh toán trùng hoặc lịch sử mâu thuẫn. Sau giao dịch, số dư tài khoản, trạng thái học phí và lịch sử phản ánh đúng kết quả cuối cùng.

## 6. Tám hạng mục phải bàn giao

| # | Hạng mục | Kết quả cần có |
|---|---|---|
| 1 | Phân tích nghiệp vụ và dữ liệu | Mô tả nghiệp vụ, dữ liệu; tối thiểu có **Use Case Diagram** và **Entity Relationship Diagram (ERD)**. |
| 2 | Thiết kế kiến trúc Microservices | Xác định các service, trách nhiệm từng service, cách giao tiếp; có **Microservices Architecture Diagram**. |
| 3 | Thiết kế REST API | Với từng chức năng, xác định **URI, HTTP Method, Input/Request, Output/Response, HTTP Status Code**. |
| 4 | Thiết kế và hiện thực cơ sở dữ liệu | Dùng SQL và/hoặc NoSQL phù hợp, có cấu trúc dữ liệu phục vụ phân hệ. |
| 5 | Lập trình các service và API | Hiện thực đầy đủ chức năng theo thiết kế và kết nối giữa các service. |
| 6 | Hiện thực transaction và concurrency | Bảo đảm nhất quán khi nhiều giao dịch dùng cùng tài khoản hoặc cùng trả một khoản học phí. |
| 7 | Lập trình giao diện tương tác | Ưu tiên **Web Application**, tích hợp API để thực hiện trọn luồng người dùng. |
| 8 | Tài liệu và trình diễn | Có hướng dẫn cài đặt, khởi chạy, sử dụng và chuẩn bị trình diễn sản phẩm. |

## Các luồng cần chứng minh khi nghiệm thu

- Đăng nhập → nhập MSSV → tra cứu → xác nhận → nhận và nhập OTP → thanh toán → kiểm tra số dư, trạng thái học phí, lịch sử và email.
- Thanh toán cho sinh viên khác.
- MSSV không tồn tại, khoản đã thanh toán, thiếu thông tin hoặc không đủ số dư: giao dịch bị chặn.
- OTP sai, hết hạn, đã dùng hoặc không thuộc giao dịch: không trừ tiền.
- Giao dịch đồng thời trên cùng tài khoản và thanh toán đồng thời cùng khoản học phí: dữ liệu cuối cùng vẫn nhất quán.

## Cấu trúc workspace

| Thư mục | Nội dung |
|---|---|
| [`src/`](src/) | Mã nguồn và [hướng dẫn chạy hệ thống đầy đủ](src/README.md). |
| [`bao-cao/`](bao-cao/) | Báo cáo, tài liệu thiết kế và sơ đồ. |
| [`de-bai/`](de-bai/) | Ba ảnh đề bài gốc. |
| [`cau-hinh-chung/`](cau-hinh-chung/) | Hợp đồng API, dữ liệu mẫu, ma trận kiểm thử và cấu hình dùng chung. |

## Bản chạy hiện tại

Hệ thống tích hợp gồm Account, Payment, Notification và giao diện React. Từ thư mục `src`, chạy `docker compose up --build -d`, rồi mở http://localhost:5173. Xem [báo cáo giữa kỳ](bao-cao/bao-cao-giua-ky-ibanking-day-du.docx), [bộ sáu sơ đồ draw.io](bao-cao/docs/ibanking-so-do-day-du.drawio) và [hướng dẫn sơ đồ](bao-cao/docs/so-do-huong-dan.md).
