# KẾT QUẢ KIỂM TRA BỘ TÀI LIỆU 1.0.0

Các kiểm tra dưới đây chạy trên tệp hợp đồng và dữ liệu, không gọi ứng dụng thực tế.

| Kiểm tra | Kết quả |
|---|---|
| OpenAPI 3.0.3 được kiểm tra bằng openapi-spec-validator | PASS |
| Số đường dẫn / operation | 9 / 10 |
| Tham chiếu và operationId | Hợp lệ, không trùng |
| Ví dụ request/response khớp schema bằng OAS30Validator | PASS: 62 ví dụ |
| Request lỗi bị schema từ chối | PASS: 9 mẫu |
| ID, quan hệ, số tiền và trạng thái dữ liệu seed | PASS |
| Dữ liệu thiếu tiền / bằng đúng tiền / đã đóng / chưa có công nợ / không tồn tại | Có đầy đủ |
| OTP example có thời gian sống 300 giây | PASS |
| Ma trận test có ID và người phụ trách | PASS: 37 case |
| Version hợp đồng, seed và ma trận test | Đồng nhất 1.0.0 |

## Giới hạn của kết quả

- Chưa hiện thực/chạy các service, frontend, database, mock hoặc SMTP.
- 37 case trong ma trận đều NOT_RUN. Đó là tiêu chí cần thực hiện, không phải 37 bài test đã pass.
- Chưa chứng minh cơ chế khóa/rollback/concurrency hay email tới inbox; phải kiểm chứng khi có sản phẩm.
- Bộ dữ liệu dùng thông tin giả; email .test phải thay bằng hộp thư nhóm kiểm soát khi nghiệm thu thật.
- Không có bảo đảm điểm số chỉ nhờ dùng bộ chốt này; báo cáo và demo phải phản ánh hiện thực đúng.
