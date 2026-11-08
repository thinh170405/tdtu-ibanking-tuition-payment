# 1. Phân tích nghiệp vụ & UML

## 1.1. Mục tiêu và phạm vi

Phân hệ đóng học phí iBanking cho phép khách hàng đăng nhập bằng tài khoản ngân hàng, xem thông tin tài khoản và số dư, tra cứu khoản học phí theo mã số sinh viên (MSSV), thanh toán **toàn bộ** khoản còn nợ, xác thực bằng OTP gửi qua email và nhận kết quả. Khách hàng có thể đóng học phí cho sinh viên khác; người trả tiền là chủ tài khoản iBanking đanđăg ng nhập. Phạm vi này không bao gồm đăng ký tài khoản hoặc thanh toán một phần.

**Quy tắc nghiệp vụ:** (R1) Mọi thao tác tra cứu số dư và thanh toán yêu cầu đăng nhập hợp lệ. (R2) Thông tin người trả tiền lấy từ tài khoản đăng nhập và chỉ hiển thị, không cho sửa trong giao dịch. (R3) Số tiền phải trả do hệ thống lấy từ khoản học phí chưa thanh toán; khách hàng không nhập số tiền tùy ý. (R4) Chỉ cho khởi tạo khi đã chấp nhận điều khoản, khoản học phí chưa được trả và số dư đủ. (R5) OTP gắn với đúng một giao dịch, hết hạn sau 5 phút và chỉ dùng thành công một lần. (R6) Khi xác nhận OTP, hệ thống kiểm tra lại số dư và trạng thái học phí, rồi cập nhật số dư, gạch nợ và giao dịch trong một thao tác nguyên tử. (R7) Cùng một khoản học phí chỉ có tối đa một giao dịch thành công; các yêu cầu đồng thời không được làm số dư âm. (R8) Email xác nhận được gửi sau khi thanh toán đã ghi nhận thành công; lỗi gửi email không đảo ngược giao dịch tài chính.

## 1.2. Tác nhân và thành phần liên quan

| Thành phần | Vai trò và tương tác | Phân loại trong Use Case Diagram |
|---|---|---|
| Người dùng (User/Khách hàng) | Chủ tài khoản iBanking; nhập thông tin đăng nhập, MSSV, chấp nhận điều khoản, xác nhận thanh toán, nhập OTP và xem kết quả. Người dùng không nhất thiết là sinh viên có khoản học phí. | Actor chính, nằm ngoài ranh giới hệ thống. |
| Hệ thống iBanking | Xác thực người dùng, cung cấp thông tin tài khoản, phối hợp tra cứu học phí, kiểm tra và xử lý giao dịch, lưu kết quả. | Hệ thống đang được mô tả; thể hiện bằng khung ranh giới, **không** vẽ thành actor của chính nó. |
| Hệ thống Email (Notification) | Nhận yêu cầu gửi OTP và email xác nhận, chuyển thư tới địa chỉ email của người trả tiền; phản hồi trạng thái gửi. | Actor phụ nếu là dịch vụ ngoài ranh giới phân hệ; nếu Notification Service nằm trong iBanking thì chỉ nhà cung cấp email ngoài là actor. |
| Cơ sở dữ liệu | Lưu tài khoản, sinh viên, học phí, giao dịch và OTP; cung cấp dữ liệu nhất quán cho các chức năng. | Kho dữ liệu nội bộ, **không** là actor UML vì không chủ động theo đuổi mục tiêu nghiệp vụ. Thể hiện trong ERD hoặc sơ đồ kiến trúc. |

## 1.3. Đặc tả Use Case

### UC01 — Đăng nhập hệ thống

- **Tác nhân chính:** Người dùng. **Mục tiêu:** Có phiên truy cập hợp lệ.
- **Điều kiện trước:** Tài khoản đã tồn tại và đang được phép sử dụng; người dùng chưa cần đăng nhập.
- **Luồng chính:** (1) Người dùng nhập username và password. (2) Hệ thống kiểm tra định dạng đầu vào, tìm tài khoản và đối chiếu mật khẩu đã băm. (3) Khi hợp lệ, hệ thống cấp phiên hoặc access token và chuyển tới màn hình tài khoản.
- **Luồng ngoại lệ/lỗi:** Thiếu dữ liệu hoặc sai định dạng: yêu cầu nhập lại. Sai username/password hoặc tài khoản bị khóa: từ chối đăng nhập, không tiết lộ trường nào sai. Dịch vụ xác thực không sẵn sàng: báo lỗi và cho phép thử lại. Phiên/token hết hạn về sau: yêu cầu đăng nhập lại.
- **Điều kiện sau:** Thành công: có phiên hợp lệ gắn với đúng người dùng. Thất bại: không cấp phiên, không thay đổi dữ liệu tài chính.

### UC02 — Tra cứu thông tin tài khoản & số dư

- **Tác nhân chính:** Người dùng. **Mục tiêu:** Biết danh tính người trả tiền và số dư khả dụng.
- **Điều kiện trước:** UC01 thành công; phiên còn hiệu lực.
- **Luồng chính:** (1) Người dùng mở màn hình tài khoản. (2) Hệ thống lấy họ tên, số điện thoại, email của tài khoản và số dư hiện tại của ví/tài khoản thanh toán. (3) Hiển thị dữ liệu ở chế độ chỉ đọc.
- **Luồng ngoại lệ/lỗi:** Phiên không hợp lệ: yêu cầu đăng nhập lại. Không tìm thấy tài khoản/ví hoặc dịch vụ dữ liệu lỗi: thông báo không thể tải; không cho tiếp tục tạo giao dịch khi chưa xác định được nguồn tiền.
- **Điều kiện sau:** Thông tin và số dư được hiển thị; không phát sinh thay đổi số dư. Số dư hiển thị chỉ mang tính tham khảo, phải được kiểm tra lại ở UC04 và UC06.

### UC03 — Tra cứu thông tin học phí sinh viên theo MSSV

- **Tác nhân chính:** Người dùng. **Mục tiêu:** Xác định đúng khoản học phí cần đóng.
- **Điều kiện trước:** Đã đăng nhập; có MSSV hợp lệ theo định dạng hệ thống (dữ liệu mẫu dùng 8 chữ số).
- **Luồng chính:** (1) Người dùng nhập MSSV. (2) Hệ thống kiểm tra định dạng, tìm sinh viên và các khoản học phí tương ứng. (3) Hiển thị họ tên sinh viên, MSSV, mã khoản, số tiền phải trả và trạng thái. (4) Chỉ khoản `UNPAID` được chọn để thanh toán.
- **Luồng ngoại lệ/lỗi:** MSSV sai định dạng: yêu cầu sửa. Không có sinh viên hoặc khoản học phí: báo không tìm thấy. Khoản đã `PAID`: vẫn có thể hiển thị để đối chiếu nhưng khóa chức năng thanh toán. Lỗi tra cứu: cho phép thử lại; không dùng kết quả cũ của MSSV khác.
- **Điều kiện sau:** Người dùng có thông tin khoản học phí hiện hành; chưa tạo giao dịch hoặc trừ tiền.

### UC04 — Khởi tạo giao dịch thanh toán học phí

- **Tác nhân chính:** Người dùng. **Mục tiêu:** Tạo yêu cầu thanh toán toàn bộ và nhận OTP.
- **Điều kiện trước:** Đã đăng nhập; đã chọn một khoản `UNPAID` từ UC03; đã chấp nhận điều khoản. Số dư hiển thị đủ để người dùng tiếp tục.
- **Luồng chính:** (1) Người dùng chọn thanh toán. (2) Hệ thống nhận mã khoản học phí và mã yêu cầu duy nhất, đọc lại số tiền từ dữ liệu học phí; không tin số tiền do giao diện gửi. (3) Kiểm tra khoản còn nợ và số dư hiện tại đủ trả **toàn bộ** số tiền. (4) Tạo giao dịch `PENDING_OTP`, sinh OTP gắn với giao dịch, lưu dạng băm với thời điểm hết hạn sau 5 phút. (5) Gửi OTP tới email của chủ tài khoản và hiển thị màn hình nhập OTP. Chưa trừ tiền ở bước này.
- **Luồng ngoại lệ/lỗi:** Chưa chấp nhận điều khoản hoặc dữ liệu sai: từ chối. Khoản đã được trả: báo xung đột. Số dư thiếu: từ chối và hiển thị số dư mới. Email không thể gửi: báo chưa thể xác thực; không trình bày giao dịch là đã thanh toán. Yêu cầu lặp cùng mã và cùng nội dung: trả lại giao dịch cũ; mã trùng nhưng nội dung khác: từ chối.
- **Điều kiện sau:** Thành công: có giao dịch chờ OTP và OTP gửi tới email; số dư/học phí chưa thay đổi. Thất bại: không tạo giao dịch có thể thanh toán hoặc không tiến tới bước xác thực.

### UC05 — Xác thực giao dịch bằng mã OTP qua email

- **Tác nhân chính:** Người dùng; hệ thống Email hỗ trợ gửi mã. **Mục tiêu:** Chứng minh quyền xác nhận giao dịch đã khởi tạo.
- **Điều kiện trước:** Có giao dịch `PENDING_OTP` của chính người dùng; OTP đã phát hành; phiên còn hiệu lực.
- **Luồng chính:** (1) Người dùng nhập mã OTP nhận qua email. (2) Hệ thống xác định giao dịch và đối chiếu mã với bản băm; kiểm tra mã chưa dùng và thời điểm hiện tại chưa vượt quá `expires_at` (5 phút từ lúc phát hành). (3) Nếu hợp lệ, hệ thống chuyển sang UC06 để hoàn tất giao dịch. OTP chỉ được đánh dấu đã dùng khi giao dịch tài chính thành công trong cùng thao tác nguyên tử.
- **Luồng ngoại lệ/lỗi:** Sai mã: từ chối, giao dịch vẫn chờ nếu còn hiệu lực. Mã hết hạn: từ chối và kết thúc khả năng sử dụng mã đó. Mã đã dùng, giao dịch không thuộc người dùng hoặc đã có kết quả cuối: từ chối, không xử lý lần hai. Lỗi kỹ thuật: không tiêu thụ OTP hoặc trừ tiền một phần; cho phép kiểm tra lại trạng thái giao dịch.
- **Điều kiện sau:** OTP hợp lệ dẫn tới UC06; mã không hợp lệ không làm thay đổi số dư hay học phí.

### UC06 — Xử lý giao dịch thành công

- **Tác nhân kích hoạt:** Hệ thống iBanking sau UC05; hệ thống Email nhận yêu cầu gửi xác nhận. **Mục tiêu:** Hoàn tất thanh toán và lưu chứng cứ.
- **Điều kiện trước:** UC05 đã xác nhận OTP hợp lệ; giao dịch đang `PENDING_OTP` và thuộc người dùng đang đăng nhập.
- **Luồng chính:** (1) Hệ thống khóa/kiểm soát đồng thời dữ liệu tài khoản và khoản học phí liên quan. (2) Đọc lại số dư và trạng thái học phí, bảo đảm số dư đủ và khoản chưa trả. (3) Trong một database transaction, trừ đúng số tiền học phí, đổi học phí sang `PAID`, đánh dấu giao dịch `SUCCESS`, ghi thời điểm và thông tin lịch sử, đánh dấu OTP đã dùng. (4) Commit; trả kết quả và số dư mới cho người dùng. (5) Sau commit, yêu cầu hệ thống Email gửi thư xác nhận có mã giao dịch, MSSV, khoản tiền và thời điểm.
- **Luồng ngoại lệ/lỗi:** Số dư đã bị giao dịch khác sử dụng: không trừ tiền, trả lỗi thiếu số dư. Khoản đã được giao dịch khác thanh toán: không trừ tiền lần hai, trả trạng thái đã đóng. Lỗi bất kỳ trước commit: rollback toàn bộ cập nhật. Lặp yêu cầu xác nhận: trả kết quả giao dịch đã xử lý, không trừ lại. Gửi email xác nhận thất bại sau commit: giữ kết quả `SUCCESS`, ghi trạng thái thông báo để gửi lại.
- **Điều kiện sau:** Thành công: số dư giảm một lần, học phí `PAID`, giao dịch và lịch sử `SUCCESS`, OTP không thể dùng lại, email xác nhận được gửi hoặc xếp hàng gửi lại. Thất bại tài chính: số dư và học phí giữ nguyên; không có lịch sử thành công giả.

## 1.4. Cấu trúc sơ đồ Use Case

Sơ đồ [Use Case Diagram](./01-phan-tich-nghiep-vu-use-case.drawio) có khung **iBanking Tuition Payment Subsystem** chứa UC01–UC06; **User** ở trái và **Email Service** ở phải. User liên kết với UC01–UC05; UC06 là xử lý nội bộ được kích hoạt sau xác thực, không phải thao tác trực tiếp của User. Quan hệ `«include»` diễn tả UC04 cần dữ liệu UC03; UC06 `«extend»` UC05 khi OTP hợp lệ. Đường liên kết tới Email Service thể hiện gửi OTP ở UC04 và thư xác nhận ở UC06. Database được thể hiện trong ERD, không đưa vào sơ đồ Use Case như actor.

## 1.5. ERD khái niệm ban đầu

Sơ đồ [Initial ERD](./01-phan-tich-nghiep-vu-erd.drawio) gồm năm thực thể cốt lõi. Đây là mô hình nghiệp vụ ban đầu; tên cột vật lý có thể điều chỉnh theo migration của từng service.

| Thực thể | Thuộc tính chính | Ràng buộc và quan hệ |
|---|---|---|
| `Users` (Tài khoản) | `user_id` PK, `username` UQ, `password_hash`, `full_name`, `email`, `phone`, `balance` | `balance >= 0`; một User có nhiều Transaction. Nếu triển khai tách dịch vụ, `balance` nên thuộc Wallet/Payment DB và `user_id` là tham chiếu logic xuyên service. |
| `Students` (Sinh viên) | `student_id` PK (MSSV), `full_name`, `program` | Một Student có nhiều Tuition theo kỳ hoặc khoản thu. Người trả tiền không bắt buộc là Student. |
| `Tuitions` (Học phí) | `tuition_id` PK, `student_id` FK, `term`, `amount`, `status`, `paid_at` | `amount > 0`; trạng thái `UNPAID/PAID`; một Tuition có thể có nhiều lần thử Transaction nhưng tối đa một lần thành công. |
| `Transactions` (Giao dịch) | `transaction_id` PK, `user_id` FK, `tuition_id` FK, `request_id`, `amount`, `status`, `created_at`, `completed_at` | `amount` bằng toàn bộ khoản học phí được chốt khi tạo; `request_id` duy nhất theo User; trạng thái `PENDING_OTP/SUCCESS/FAILED/EXPIRED`; một User và một Tuition đều có thể gắn với nhiều lần thử. |
| `OTPs` | `otp_id` PK, `transaction_id` FK/UQ, `code_hash`, `issued_at`, `expires_at`, `used_at` | Mỗi giao dịch có tối đa một OTP hiện hành trong mô hình ban đầu; `expires_at = issued_at + 5 phút`; không lưu mã thô; `used_at` chỉ được đặt một lần khi thanh toán thành công. |

**Bội số:** `Users 1—N Transactions`; `Students 1—N Tuitions`; `Tuitions 1—N Transactions`; `Transactions 1—0..1 OTPs`. Cần unique constraint hoặc khóa phù hợp để chặn hai giao dịch `SUCCESS` cùng `tuition_id`; đồng thời kiểm tra và cập nhật số dư nguyên tử. Giữa các database của microservice, các khóa tham chiếu là liên kết logic, không tạo foreign key xuyên database. Dữ liệu gửi email có thể được lưu thêm ở bảng thông báo/outbox khi triển khai, nhưng nằm ngoài năm thực thể cốt lõi của ERD ban đầu.
