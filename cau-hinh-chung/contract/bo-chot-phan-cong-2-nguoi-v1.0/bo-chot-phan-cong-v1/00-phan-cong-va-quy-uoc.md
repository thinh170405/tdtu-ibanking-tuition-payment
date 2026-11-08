# BỘ CHỐT PHÂN CÔNG VÀ HỢP ĐỒNG DỰ ÁN iBANKING - 1.0.0

## 1. Kết luận rà soát và cách sử dụng

Danh sách API trước đã có các chức năng chính nhưng chưa đủ chặt để hai người hiện thực độc lập rồi ghép ngay: còn thiếu schema máy đọc được, dữ liệu thử thiếu tiền/bằng đúng tiền, thứ tự trả lỗi, xử lý request lặp đang chạy, trạng thái terminal và cách thử OTP/concurrency. Bản 1.0.0 bổ sung những phần đó.

Đây là bản chốt thay các ví dụ sơ bộ trước. Các tệp đi kèm là hợp đồng và kịch bản kiểm thử, không phải phần mềm đã được lập trình hoặc kết quả đã chạy.

| Tệp | Cách dùng |
|---|---|
| 00-phan-cong-va-quy-uoc.md | Giao việc, quy tắc nghiệp vụ, báo cáo, mock và ghép nối |
| 01-openapi.json | Nguồn chuẩn cho endpoint, request/response, kiểu dữ liệu, HTTP status và xác thực; mở/import bằng công cụ hỗ trợ OpenAPI |
| 02-du-lieu-mau.json | A seed users; B seed các mảng dữ liệu tài chính; dùng cùng ID |
| 03-ma-tran-kiem-thu.json | 37 test case, setup/steps/expected, người phụ trách và hook test; mọi case ban đầu NOT_RUN |
| 04-cau-hinh.env.example | Tên biến và địa chỉ đã thống nhất; thay placeholder bằng cấu hình máy mình |
| 05-kiem-tra-bo-tai-lieu.md | Kết quả kiểm tra cấu trúc hợp đồng/dữ liệu, không phải kết quả test sản phẩm |

Nếu có điểm cần làm rõ về dữ liệu giao tiếp, lấy 01-openapi.json làm chuẩn. Quy tắc chuyển trạng thái và transaction lấy tài liệu 00 này làm chuẩn; 03 mô tả bằng chứng cần có. Khi sửa hợp đồng phải sửa cả các tệp liên quan và tăng version; không âm thầm đổi tên ở một phía.

## 2. Kiến trúc và việc chia độc lập

- A: Account Service + Notification Service + toàn bộ frontend + kiểm thử và báo cáo phần A.
- B: Payment Service + dữ liệu tài chính + OTP + transaction/concurrency + kiểm thử và báo cáo phần B.
- Ba backend chạy riêng và giao tiếp qua HTTP. Payment sở hữu ví, công nợ, giao dịch, OTP và công việc gửi email thành công. Account sở hữu đăng nhập/hồ sơ; Notification gửi mail.
- Các cập nhật tài chính nằm trong một database của Payment để sử dụng transaction cục bộ. Không có bước trừ tiền ở Account rồi chờ Payment cập nhật học phí.
- Mỗi người nhận bộ chốt này là bắt đầu được; không cần đợi code/sơ đồ/báo cáo của người kia.

### Gói A

| Mã | Nhiệm vụ A tự thực hiện | Đầu ra và tiêu chí hoàn thành |
|---|---|---|
| A1 | Phân tích yêu cầu, actor, use case | Use Case Diagram có nguồn; đặc tả đăng nhập, tra cứu, thanh toán, OTP, kết quả/lịch sử; điều kiện trước/sau và lỗi |
| A2 | Thiết kế kiến trúc theo bộ chốt | Architecture Diagram có nguồn; thể hiện frontend, 3 service, data store, email ngoài, trách nhiệm và cách giao tiếp |
| A3 | Database và API Account | Migration/seed users, password hash, login, profile, kiểm tra token; schema đúng OpenAPI |
| A4 | Notification Service | API nội bộ, hai mẫu email, X-Internal-Key, lưu messageId/kết quả, xử lý gửi lặp và lỗi; thử được bằng request mẫu |
| A5 | Toàn bộ giao diện | Login, hồ sơ/số dư, tự tra cứu khi MSSV đủ 8 chữ số, thanh toán toàn bộ, điều khoản, OTP, kết quả/lịch sử |
| A6 | Mock Payment và test A | A tự tạo mock từ OpenAPI; thử UI thành công/lỗi, tránh response tra cứu cũ ghi đè; test Account/mail và lưu bằng chứng |
| A7 | Đóng gói riêng A | Source, Dockerfile/lệnh chạy, biến cấu hình, README A, migration/seed; chạy được cùng Payment mock |
| A8 | Báo cáo/slide A | Viết đầy đủ các phần A ở mục 9, có sơ đồ/ảnh/bảng API và kết quả test riêng; không đợi B viết |

### Gói B

| Mã | Nhiệm vụ B tự thực hiện | Đầu ra và tiêu chí hoàn thành |
|---|---|---|
| B1 | Phân tích dữ liệu và ERD | ERD có nguồn, từ điển dữ liệu, khóa/quan hệ, constraints, trạng thái, quyền sở hữu dữ liệu |
| B2 | Database Payment | Migration/seed wallets/students/tuitions/payments; dữ liệu bền; ràng buộc tài chính và idempotency |
| B3 | API đọc dữ liệu | Wallet, tra cứu, list/detail payment; lọc đúng người dùng và đúng schema OpenAPI |
| B4 | Tạo giao dịch và OTP | Kiểm tra điều kiện, requestId, sinh/lưu OTP, chống trùng đang hiệu lực, TTL 300 giây; gọi Notification theo contract |
| B5 | Xác nhận thanh toán | Khóa và kiểm tra lại, trừ tiền, gạch nợ, lịch sử, tiêu thụ OTP nguyên tử; đúng state/error ở mục 6 |
| B6 | Transaction, concurrency và lỗi mail | Hai bài đồng thời; confirm/create lặp; rollback; lưu email job sau commit để thử lại, không chạy lại thanh toán |
| B7 | Mock Notification, token và test B | B tự tạo token đúng claim bằng khóa test riêng; mock mail thu nhận OTP trong test và mô phỏng lỗi; viết test tài chính độc lập, có bằng chứng |
| B8 | Đóng gói, báo cáo/slide B | Source, Dockerfile/lệnh chạy, config, README B, migration/seed, test; các chương B đầy đủ theo mục 9 |

A nhận khối lượng UI, tài khoản, email và tài liệu tương ứng; B nhận độ khó tài chính và tính nhất quán. Đánh giá đóng góp bằng gói việc đã nghiệm thu và thời gian thực tế, không đếm số API hoặc số commit.

## 3. Quy ước chung và API

- REST, JSON UTF-8; tên trường lowerCamelCase; API công khai có prefix /api/v1.
- Mọi trường body đều bắt buộc theo schema; không nhận trường ngoài schema. Sai kiểu/thiếu/thừa trường: 400 VALIDATION_ERROR.
- ID, MSSV, điện thoại, OTP là string. Dữ liệu demo quy ước MSSV 8 chữ số; OTP 6 chữ số.
- Tiền là integer VND trong khoảng số nguyên an toàn của JSON/JavaScript; balance >= 0, amount > 0. Backend tính tiền bằng kiểu integer phù hợp trong database.
- Date-time UTC ISO 8601; UI hiển thị giờ Việt Nam. iat/exp của JWT riêng dùng Unix time giây.
- Thành công trả object trực tiếp; danh sách trả {"items": []}; lỗi trả đúng {"code": "...", "message": "..."}.
- paidAt, otpExpiresAt, failureCode có thể null theo schema nhưng luôn có trường trong Payment response.
- List payment là toàn bộ dữ liệu mẫu của người đang đăng nhập, kể cả pending/failed/expired; sắp createdAt giảm dần, nếu bằng nhau paymentId tăng dần. Chưa cần phân trang cho bài này.

| Chủ | Method / endpoint | Thành công |
|---|---|---|
| A | POST /api/v1/auth/login | 200 tokenType Bearer, accessToken, expiresIn=3600 |
| A | GET /api/v1/users/me | 200 userId/fullName/phone/email |
| B | GET /api/v1/wallet | 200 userId/balance/currency |
| B | GET /api/v1/tuition/{mssv} | 200 studentId/studentName/tuitionId/amount/currency/status/paidAt |
| B | POST /api/v1/payments | 201 Payment mới; 200 request lặp đã khởi tạo thành công |
| B | GET /api/v1/payments | 200 {items: Payment[]} |
| B | GET /api/v1/payments/{paymentId} | 200 Payment |
| B | POST /api/v1/payments/{paymentId}/confirm | 200 Payment thành công hoặc kết quả SUCCESS đã có |
| A | POST /internal/v1/notifications/email | 200 messageId/status SENT |
| Mỗi service | GET /api/v1/health | 200 status UP và service name |

Chốt tên trường: termsAccepted; không dùng acceptedTerms. Chốt login: expiresIn, không dùng expiresAt. Confirm trả Payment, không trả balance; UI gọi lại wallet để lấy số dư mới nhất.

Create body:
```json
{"tuitionId":"HP001","termsAccepted":true,"requestId":"2e9d1c7a-7d45-4e1c-9f80-5ff806ef0d11"}
```

Confirm body:
```json
{"otp":"038271"}
```

Payment response chung:
```json
{
  "paymentId":"pay_example_001",
  "tuitionId":"HP001",
  "studentId":"52600001",
  "studentName":"Nguyễn Văn An",
  "amount":7000000,
  "currency":"VND",
  "status":"PENDING_OTP",
  "createdAt":"2026-11-02T08:00:00Z",
  "otpExpiresAt":"2026-11-02T08:05:00Z",
  "paidAt":null,
  "failureCode":null
}
```

Không trả OTP/hash OTP, khóa, password/hash hoặc email job nội bộ qua các API nghiệp vụ công khai. userId/requestId trong seed payment là thuộc tính lưu nội bộ, không tự thêm vào response vì response có schema riêng.

## 4. Xác thực, lỗi và an toàn dữ liệu

- JWT HS256, 3600 giây; claim sub=userId, email, iss=ibanking-demo, aud=ibanking-api, iat/exp theo giây.
- Account và Payment kiểm tra chữ ký, thuật toán chỉ cho phép HS256, issuer, audience và thời hạn. Decode không thay cho kiểm tra token.
- API người dùng gửi Authorization: Bearer <token>. 401 của API này có WWW-Authenticate: Bearer. Login sai trả 401 INVALID_CREDENTIALS.
- Trong lúc làm riêng A/B dùng khóa test riêng; khi ghép dùng cùng JWT_SECRET ngẫu nhiên ít nhất 32 byte. Không đưa JWT_SECRET vào frontend hoặc commit khóa thật.
- API nội bộ mail dùng X-Internal-Key riêng; thiếu/sai trả 403 FORBIDDEN. Frontend không biết khóa này.
- Người nộp, email người nộp lấy từ danh tính đã xác thực. Profile hiển thị chỉ đọc. Không có chức năng đăng ký hoặc sửa hồ sơ trong phạm vi.
- Các request tạo payment kèm amount, balance, payerUserId bị 400 vì trường ngoài schema. Thanh toán một phần không được thực hiện.
- Payment chi tiết/confirm kiểm tra owner; list chỉ dữ liệu của sub. Không có transaction khi chưa xác thực hợp lệ.
- Không log token/OTP/password/khóa ở bản thật. HTTPS khi triển khai bên ngoài local.

| HTTP | Các code đã chốt |
|---:|---|
| 400 | VALIDATION_ERROR |
| 401 | INVALID_CREDENTIALS, UNAUTHORIZED |
| 403 | FORBIDDEN |
| 404 | STUDENT_NOT_FOUND, TUITION_NOT_FOUND, PAYMENT_NOT_FOUND, WALLET_NOT_FOUND |
| 409 | TUITION_ALREADY_PAID, REQUEST_ID_CONFLICT, REQUEST_IN_PROGRESS, OTP_DELIVERY_PENDING, MESSAGE_ID_CONFLICT |
| 422 | INSUFFICIENT_BALANCE, INVALID_OTP, OTP_EXPIRED |
| 503 | NOTIFICATION_UNAVAILABLE |
| 500 | INTERNAL_ERROR |

Message là tiếng Việt để hiển thị; code ổn định cho UI xử lý. API cụ thể nhận mã nào đã ghi trong OpenAPI.

## 5. Dữ liệu dùng ngay, không cần tự đặt lại

Tài khoản demo1/u1/Nguyễn Văn An và demo2/u2/Trần Thị Bình; mật khẩu mẫu Demo!2026; mỗi ví hiện tại 10 triệu VND.

| MSSV | Tên | tuitionId | Số tiền | Mục đích |
|---|---|---|---:|---|
| 52600001 | Nguyễn Văn An | HP001 | 7.000.000 | Thành công, trả cho mình, concurrency |
| 52600002 | Trần Thị Bình | HP002 | 7.000.000 | Trả hộ, cùng ví hai khoản |
| 52600003 | Lê Minh Chi | HP003 | 5.000.000 | Đã PAID, có lịch sử pay_seed_001 của u2 |
| 52600004 | Phạm Quốc Dũng | HP004 | 11.000.000 | Thiếu số dư ngay trên seed chuẩn |
| 52600005 | Võ Thu Giang | HP005 | 10.000.000 | Số dư bằng đúng học phí, sau đóng còn 0 |
| 52600006 | Đặng Ngọc Hà | Không có | Không có | Sinh viên có nhưng chưa có khoản học phí: 404 TUITION_NOT_FOUND |
| 52699999 | Không tồn tại | Không có | Không có | 404 STUDENT_NOT_FOUND |

- Email .test trong JSON chỉ là placeholder. Cấu hình DEMO_EMAIL_1/2 bằng hộp thư nhóm kiểm soát khi test thật, seed/cập nhật email và login lại để token khớp.
- passwordForSeeding phải hash khi import; không lưu nguyên văn. Dữ liệu giả không dùng làm tài khoản triển khai thật.
- Số dư 10 triệu là trạng thái hiện tại, không trừ lại giao dịch lịch sử khi import.
- Seed một lần theo trạng thái; không gọi lại luồng thanh toán cho pay_seed_001.
- Reset trước mỗi case độc lập. Không cung cấp API public sửa số dư, ép OTP hoặc reset DB để phục vụ test.
- Không seed OTP còn hiệu lực bằng ngày cố định. Mỗi test tạo OTP ở runtime; thời gian và mã ví dụ trong tài liệu không phải OTP dùng thật.

## 6. Quy tắc nghiệp vụ và thứ tự xử lý chốt

### 6.1. Tra cứu và điều kiện UI

- Khi nhập đủ 8 chữ số, frontend tự tra cứu; không bắt buộc người dùng bấm thêm nút tra cứu.
- Khi đổi MSSV, xóa thông tin học phí và ngữ cảnh thanh toán/OTP cũ. Không để response tra cứu cũ ghi đè MSSV mới.
- Thông tin người nộp từ users/me, chỉ đọc; số dư từ wallet; học phí từ tuition.
- Nút tạo/xác nhận bước thanh toán chỉ bật khi đã có dữ liệu hợp lệ: công nợ UNPAID, số dư >= amount, đồng ý điều khoản, không đang gửi request. Kiểm tra UI không thay cho kiểm tra lại tại server.

### 6.2. Tạo payment và idempotency

1. Xác thực, validate body (kể cả cấm trường ngoài schema).
2. Kiểm tra (userId, requestId). Cùng ID/body đã khởi tạo xong trả 200 Payment hiện tại; không tạo OTP/mail mới. Cùng ID khác body trả 409 REQUEST_ID_CONFLICT. Khác thứ tự key JSON không được coi là khác body.
3. Nếu request đó đang khởi tạo/gửi OTP, trả 409 REQUEST_IN_PROGRESS và Retry-After: 1. Frontend giữ nguyên requestId để thử lại, không tự tạo ID mới khi chỉ timeout.
4. Với request mới: ví phải tồn tại, học phí phải tồn tại. Khoản đã PAID ưu tiên 409 TUITION_ALREADY_PAID; sau đó mới kiểm tra thiếu tiền 422 INSUFFICIENT_BALANCE.
5. Server tự đọc amount; tạo payment PENDING_OTP, OTP 6 số ngẫu nhiên an toàn, hết hạn sau 300 giây từ lúc phát hành, lưu trạng thái gửi OTP nội bộ.
6. Gọi Notification bằng messageId otp:<paymentId>. Chỉ trả 201 khi provider chấp nhận gửi và B đã ghi nhận OTP delivery thành công. Bước này chưa trừ tiền/giữ chỗ tiền.
7. Nếu gửi thất bại/timeout: FAILED, failureCode NOTIFICATION_UNAVAILABLE, vô hiệu OTP, 503. Cùng requestId giữ lỗi 503; người dùng chủ động thử lần mới mới tạo requestId mới.
8. Các request khởi tạo dở dang vì Payment khởi động lại trước khi ghi nhận gửi xong phải được kết thúc FAILED/NOTIFICATION_UNAVAILABLE và vô hiệu OTP. Không để request in-progress mắc kẹt vô hạn hoặc vô tình thanh toán bằng OTP không xác định trạng thái gửi.

Payment có thể được tạo đồng thời cho cùng khoản học phí hoặc cùng ví; kiểm tra ban đầu không bảo đảm khoản đó vẫn thanh toán được sau thời gian nhập OTP. Phải kiểm tra lại khi confirm.

### 6.3. Xác nhận và thứ tự lỗi

1. Xác thực -> tìm payment -> kiểm tra owner -> validate body.
2. Khóa payment; nếu SUCCESS trả lại 200 kết quả cũ. Đây là đọc kết quả, không phải xác thực OTP thành công lần thứ hai. Body vẫn phải đúng định dạng.
3. Nếu EXPIRED trả 422 OTP_EXPIRED. Nếu FAILED trả code nghiệp vụ đã lưu (409/422/503 tương ứng), không chạy lại. Thiếu tiền/thanh toán trùng muốn thử mới phải tạo giao dịch mới.
4. Với PENDING_OTP nhưng chưa ghi nhận gửi OTP xong: 409 OTP_DELIVERY_PENDING và Retry-After: 1.
5. Khóa ví rồi khóa khoản học phí theo cùng thứ tự ở mọi nhánh. Sau khi chờ khóa, lấy thời gian server và kiểm tra lại hạn OTP. serverNow >= otpExpiresAt là hết hạn; đúng giây 300 đã hết hạn.
6. OTP hết hạn: EXPIRED/failureCode OTP_EXPIRED, vô hiệu mã, trả 422; không trừ tiền. OTP sai (kể cả mã của giao dịch khác): 422 INVALID_OTP, vẫn PENDING_OTP, không trừ tiền.
7. OTP hợp lệ nhưng khoản học phí đã PAID: FAILED/TUITION_ALREADY_PAID, vô hiệu OTP, 409. Nếu khoản chưa PAID nhưng số dư thiếu: FAILED/INSUFFICIENT_BALANCE, vô hiệu OTP, 422. Trường hợp cả hai cùng không hợp lệ, ưu tiên TUITION_ALREADY_PAID.
8. Hợp lệ: trong cùng transaction trừ tiền, đánh dấu học phí PAID, payment SUCCESS, paidAt, tiêu thụ OTP và tạo công việc email thành công. Commit rồi trả 200.
9. Lỗi kỹ thuật giữa cập nhật: rollback toàn bộ, 500 INTERNAL_ERROR. Nếu chưa hết hạn, payment vẫn PENDING_OTP, OTP chưa tiêu thụ; có thể retry. Không để debit đã lưu nhưng công nợ/lịch sử chưa lưu.

Các trạng thái cuối phải được commit đúng cả khi trả lỗi nghiệp vụ. Tránh ném exception khiến database rollback luôn việc đánh dấu FAILED/EXPIRED. Lỗi kỹ thuật thì phải rollback toàn bộ.

Khi GET detail/list, chuẩn hóa payment PENDING_OTP đã quá hạn thành EXPIRED/OTP_EXPIRED và vô hiệu OTP; không thay đổi tiền. Các thao tác này phải an toàn nếu có confirm đang chạy đồng thời.

### 6.4. OTP và ràng buộc tài chính

- OTP gắn paymentId và người sở hữu qua payment. Không dùng OTP của giao dịch khác, kể cả cùng user.
- Mã của hai giao dịch đang có hiệu lực phải khác nhau trên toàn Payment Service, không chỉ khác trong một user. Dùng bảo vệ tại data store cho vùng mã đang hiệu lực, xử lý collision bằng sinh lại. Test cố ý gây collision.
- Hết hạn/FAILED/đã tiêu thụ thì OTP không được dùng để thực hiện mới. Mã đã hết hiệu lực có thể được tái sử dụng ở tương lai, nhưng không làm OTP cũ hợp lệ lại.
- Có constraints cho số dư không âm, số tiền dương, requestId duy nhất trong user và không có hai SUCCESS cho cùng tuitionId. Pending/failed của cùng tuitionId được phép tồn tại.
- Không dùng khóa trong RAM một tiến trình làm bảo vệ concurrency duy nhất. Dùng transaction/row lock và constraints tại database Payment.

### 6.5. Email và ranh giới transaction

- Không giữ khóa tài chính trong lúc gọi SMTP/Notification.
- OTP mail gửi người nộp; trả hộ sinh viên khác vẫn gửi người nộp.
- Sau transaction thành công, worker B xử lý job email success:<paymentId> đã lưu cùng commit. Provider lỗi thì giữ PENDING, thử lại mỗi 30 giây và sau restart; không chạy lại payment.
- Notification A lưu messageId, nội dung chuẩn hóa và kết quả. Đã SENT cùng nội dung thì 200 cũ, đang xử lý 409 REQUEST_IN_PROGRESS, khác nội dung 409 MESSAGE_ID_CONFLICT. Nếu lần trước gửi lỗi thì cho retry cùng ID/nội dung.
- Provider chấp nhận gửi không đồng nghĩa chắc chắn tới inbox. Một timeout quanh SMTP có thể khiến email lặp; mục tiêu tài chính vẫn là không trừ tiền/lưu SUCCESS hai lần. Test T34 chỉ khẳng định không gọi lại provider cho messageId đã ghi nhận SENT.

### 6.6. Bảng trạng thái Payment response

| status | paidAt | failureCode | Tác động tiền |
|---|---|---|---|
| PENDING_OTP | null | null | Chưa trừ |
| SUCCESS | Date-time thật | null | Trừ đúng một lần |
| EXPIRED | null | OTP_EXPIRED | Chưa trừ |
| FAILED | null | INSUFFICIENT_BALANCE, TUITION_ALREADY_PAID hoặc NOTIFICATION_UNAVAILABLE | Không trừ cho giao dịch này |

otpExpiresAt luôn có ở payment runtime đã phát hành OTP; lịch sử seed có thể null. createdAt là lúc tạo, paidAt là lúc thành công, không phải thời gian gửi email.

## 7. Mock và cách làm riêng

- A tự viết/chạy Payment mock từ 01-openapi.json ở cổng 8089; mock có thành công, các lỗi, lịch sử, trạng thái OTP. OTP cố định 123456 chỉ dùng ở mock A.
- B tự viết/chạy Notification mock ở 8090; thu nhận OTP từ request trong test và điều khiển success/failure/delay. B tự tạo JWT đúng claim bằng khóa test riêng, không chờ A.
- Mock giữ đúng schema/status/path. Không làm thêm payment engine giả đầy đủ; đủ các kịch bản phần mình cần thử.
- Test clock/RNG/fault injection chỉ là hook trong test harness hoặc cấu hình test adapter, không thêm API public sửa giờ/OTP/số dư.
- Kết quả UI với mock chỉ chứng minh UI. Kết quả backend với mail mock chưa chứng minh email tới inbox. T35 bắt buộc dùng service và email thật.

## 8. Ghép source và ghép service

| Thành phần | Local | Khi caller ở Docker Compose |
|---|---|---|
| Frontend | http://localhost:5173 | Trình duyệt vẫn gọi các cổng publish localhost |
| Account | http://localhost:8081 | http://account:8081 |
| Payment | http://localhost:8082 | http://payment:8082 |
| Notification | http://localhost:8083 | http://notification:8083 |

Trong container, localhost là chính container đó. Frontend chạy trong trình duyệt không dùng hostname Docker như payment hoặc notification.

Quy trình cuối:

1. Ghép thư mục/nhánh; giữ services/account, services/payment, services/notification và frontend riêng.
2. Import seed chung vào database mỗi service, đồng bộ ID/email thật. Không trừ lại lịch sử mẫu.
3. Ghép cấu hình JWT_SECRET và INTERNAL_API_KEY, khởi chạy ba service. Cho CORS từ origin frontend local, GET/POST/OPTIONS và headers Authorization, Content-Type; không đưa khóa backend ra frontend.
4. A đổi PAYMENT_API_BASE_URL từ http://localhost:8089/api/v1 sang http://localhost:8082/api/v1.
5. B đổi NOTIFICATION_BASE_URL từ http://localhost:8090 sang http://localhost:8083; trong container dùng http://notification:8083. Đăng nhập lại lấy token thật của Account.
6. Login thật -> wallet thật -> tra cứu -> create -> email OTP -> confirm -> wallet/tuition/history -> email thành công.
7. Reset seed, chạy hai bài concurrency và các nhánh lỗi. Lưu kết quả thực tế, không ghi các expected trong 03 thành kết quả đã đạt.
8. Ghép báo cáo/README/Compose/slide; sửa các khác biệt phát hiện được. Mỗi người sửa code service mình; A không sửa trực tiếp dữ liệu của B để né lỗi.

## 9. Phân công báo cáo đầy đủ

| Chương cuối | A viết độc lập | B viết độc lập | Công việc ghép |
|---|---|---|---|
| 1. Giới thiệu, phạm vi và yêu cầu | Mục tiêu, actor, chức năng/phi chức năng, giới hạn mô phỏng | Cung cấp giới hạn nghiệp vụ tài chính nếu có | A ghép, cả hai rà soát |
| 2. Phân tích nghiệp vụ | Use Case Diagram, đặc tả luồng chính/lỗi, trước/sau | Quy tắc thanh toán, OTP và trạng thái | Ghép phần quy tắc của B vào use case A |
| 3. Kiến trúc | Architecture Diagram theo contract, trách nhiệm/giao tiếp/data ownership | Giải thích ranh giới transaction của Payment và dữ liệu tài chính | Cập nhật theo service thực tế |
| 4. Database | Schema Account, migration/seed, constraints | ERD tổng thể theo dữ liệu đã biết, Payment schema, từ điển, constraints/persistence | B hoàn thiện ERD với schema Account A bàn giao |
| 5. REST API | Account và Notification | Payment | Ghép bảng và đối chiếu 01-openapi.json |
| 6. Hiện thực | Account, mail, UI, loading/validation/lỗi, ảnh màn hình | Lookup/payment/OTP, sequence thanh toán, cập nhật nguyên tử và email job | Chụp lại bằng service thật |
| 7. Transaction/concurrency | Chạy kiểm chứng, bổ sung ảnh UI nếu cần | Cơ chế DB thực tế, thứ tự khóa, rollback, collision/idempotency và hai bài concurrency | Cả hai đọc và giải thích được |
| 8. Kiểm thử | Test Account/Notification/UI và T35 | Test Payment/OTP/DB/concurrency | Ghép bảng expected/actual, log và dữ liệu trước/sau |
| 9. Cài đặt và sử dụng | README A, cấu hình A, hướng dẫn UI, Compose tổng | README B, lệnh DB/seed/reset/test B, Dockerfile Payment | A ghép README, B thử cài lại |
| 10. Kết luận và đóng góp | Kết quả/hạn chế phần A, tổng hợp định dạng | Kết quả/hạn chế phần B, rà soát bằng chứng kỹ thuật | Ghép bảng đóng góp thực tế và slide |

Mỗi người bàn giao phần đã viết hoàn chỉnh có hình, chú thích và kết quả riêng. Phần phụ thuộc tích hợp được ghi là thiết kế/kiểm thử riêng cho đến khi chạy thật; không bắt người kia viết thay toàn bộ.

## 10. Đối chiếu đề và rubric

| Tiêu chí | Điểm | Bằng chứng và người chủ trì |
|---|---:|---|
| Phân tích nghiệp vụ & UML | 1.0 | A Use Case; B ERD; giải thích entity và nghiệp vụ |
| Microservices | 1.5 | A sơ đồ, cả hai chứng minh service chạy riêng/giao tiếp, DB và external mail |
| REST API | 1.0 | Mỗi người hiện thực/tài liệu API mình theo OpenAPI, validation và errors |
| Database & persistence | 1.0 | A Account DB; B Payment DB, constraints/seed/restart |
| Chức năng & workflow | 2.0 | A login/profile/UI/email; B lookup/payment/OTP/update/history |
| Transaction & concurrency | 1.5 | B hiện thực; A chạy lại T21/T22 và kiểm tra dữ liệu |
| UI & integration | 0.5 | A toàn luồng thật, tự tra cứu, trạng thái/nút đúng |
| Documentation/deployment/demo | 1.5 | Cả hai phần mình; A ghép hướng dẫn/Compose; B thử lại và cung cấp bằng chứng |

Ma trận kiểm thử bao phủ đăng nhập, hồ sơ, tự tra cứu, trả cho mình/người khác, full payment, thiếu/bằng số dư, OTP gắn giao dịch/duy nhất/TTL/tiêu thụ, cập nhật nguyên tử, email, hai bài đồng thời, persistence và hướng dẫn chạy. Bản hợp đồng giúp thống nhất việc hiện thực; không tự chứng minh chương trình sẽ đạt nếu chưa chạy kiểm thử.

## 11. Điều kiện chốt nộp

- [ ] A/B đều chạy riêng được bằng mock/token test trước khi ghép, có README và báo cáo phần mình.
- [ ] Khi ghép không còn mock trong luồng demo, token/mail/API thật hoạt động.
- [ ] Tất cả test được đánh dấu actual/pass/fail sau khi chạy; hai bài đồng thời có bằng chứng thực sự đồng thời.
- [ ] Tiền, học phí, lịch sử và OTP phản ánh cùng kết quả; không có cập nhật dở dang.
- [ ] Sơ đồ, API docs, ảnh, source và cấu hình đúng cùng version; không ghi kết quả dự kiến thành kết quả thực tế.
- [ ] Bộ nộp có source, report, slide, sơ đồ nguồn, OpenAPI, migration/seed, test/log, README và cấu hình mẫu.
- [ ] Mỗi người trình bày phần mình và hiểu toàn bộ luồng.

## 12. Nguồn đối chiếu

- Đề dự án trong các ảnh người dùng cung cấp và rubric-midterm.pdf gồm ba trang đã đọc.
- [OpenAPI 3.0.3](https://spec.openapis.org/oas/v3.0.3)
- [HTTP status semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [JWT](https://www.rfc-editor.org/rfc/rfc7519.html)
- [Bearer token](https://www.rfc-editor.org/rfc/rfc6750.html)
- [Docker Compose networking](https://docs.docker.com/compose/how-tos/networking/)

Tên route, dữ liệu giả, cổng, thời hạn JWT, quy tắc requestId và kiến trúc ba service là lựa chọn thiết kế của nhóm cho bài này. Đây không phải tuyên bố các chuẩn HTTP/OpenAPI bắt buộc đúng các lựa chọn đó.
