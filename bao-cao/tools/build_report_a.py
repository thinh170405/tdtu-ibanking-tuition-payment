from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'bao-cao-phan-A-ibanking.docx'
TMP = ROOT / 'tmp' / 'docx'
TMP.mkdir(parents=True, exist_ok=True)
FONT = 'C:/Windows/Fonts/arial.ttf'

def diagram(path, nodes, edges, size=(1500, 650)):
    im = Image.new('RGB', size, 'white')
    d = ImageDraw.Draw(im)
    title = ImageFont.truetype(FONT, 35)
    body = ImageFont.truetype(FONT, 26)
    for label, (x1,y1,x2,y2), fill in nodes:
        d.rounded_rectangle((x1,y1,x2,y2), radius=20, fill=fill, outline='#4C6573', width=3)
        box = d.textbbox((0,0), label, font=body)
        d.text(((x1+x2-box[2])/2,(y1+y2-box[3])/2), label, fill='#102A3A', font=body)
    for (x1,y1),(x2,y2),label in edges:
        d.line((x1,y1,x2,y2), fill='#36596B', width=4)
        import math
        a=math.atan2(y2-y1,x2-x1)
        p1=(x2-16*math.cos(a-.5),y2-16*math.sin(a-.5))
        p2=(x2-16*math.cos(a+.5),y2-16*math.sin(a+.5))
        d.polygon([(x2,y2),p1,p2], fill='#36596B')
        if label:
            d.text(((x1+x2)/2-20,(y1+y2)/2-30),label,fill='#36596B',font=ImageFont.truetype(FONT,18))
    im.save(path)

arch=TMP/'architecture.png'
diagram(arch,[
    ('Giao diện React',(30,255,245,365),'#E6F2F8'),
    ('Account Service',(360,55,650,160),'#E7F0F5'),
    ('Payment Service B',(360,255,650,365),'#E7F0F5'),
    ('Notification Service',(790,255,1110,365),'#E7F0F5'),
    ('Account DB',(790,55,1110,160),'#F0F3F5'),
    ('Payment DB',(380,500,630,590),'#F0F3F5'),
    ('Notification DB',(810,500,1090,590),'#F0F3F5'),
    ('SMTP',(1230,255,1470,365),'#F7F2E9'),
],[((245,275),(360,110),'JWT'),((245,310),(360,310),'JWT'),((650,110),(790,110),''),((650,310),(790,310),'API nội bộ'),((1110,310),(1230,310),'SMTP'),((505,365),(505,500),''),((950,365),(950,500),'')])

uc=TMP/'usecase.png'
diagram(uc,[
    ('Người nộp',(30,255,260,365),'#E6F2F8'),
    ('Đăng nhập',(390,20,680,110),'#F0F3F5'),
    ('Xem hồ sơ, số dư',(390,135,680,225),'#F0F3F5'),
    ('Tra cứu học phí',(390,250,680,340),'#F0F3F5'),
    ('Tạo giao dịch',(390,365,680,455),'#F0F3F5'),
    ('Nhập OTP',(835,365,1125,455),'#F0F3F5'),
    ('Kết quả, lịch sử',(835,480,1125,570),'#F0F3F5'),
    ('Hệ thống email',(1215,365,1480,455),'#F7F2E9'),
],[((260,275),(390,65),''),((260,290),(390,180),''),((260,310),(390,295),''),((260,330),(390,410),''),((680,410),(835,410),''),((1125,410),(1215,410),''),((975,455),(975,480),'')])

doc=Document()
sec=doc.sections[0]
sec.top_margin=Cm(2.2); sec.bottom_margin=Cm(2.0)
sec.left_margin=Cm(2.3); sec.right_margin=Cm(2.1)
styles=doc.styles
styles['Normal'].font.name='Arial'; styles['Normal'].font.size=Pt(10.5)
styles['Normal'].paragraph_format.space_after=Pt(7)
for n,size in [('Title',21),('Heading 1',14),('Heading 2',11.5)]:
    st=styles[n]; st.font.name='Arial'; st.font.size=Pt(size); st.font.bold=True; st.font.color.rgb=RGBColor(0,0,0)
    st.paragraph_format.space_before=Pt(14 if n!='Title' else 0)
    st.paragraph_format.space_after=Pt(8)
title_ppr=styles['Title']._element.get_or_add_pPr()
for border in title_ppr.findall(qn('w:pBdr')):
    title_ppr.remove(border)

def p(text='', style=None):
    return doc.add_paragraph(text, style)
def h(text, level=1):
    doc.add_heading(text, level)
def bullet(text):
    doc.add_paragraph(text, style='List Bullet')
def table(headers, rows, widths=None):
    t=doc.add_table(rows=1, cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.style='Table Grid'
    for i,v in enumerate(headers): t.rows[0].cells[i].text=v
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,v in enumerate(row): cells[i].text=str(v)
    for ri,row in enumerate(t.rows):
        for ci,cell in enumerate(row.cells):
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcPr=cell._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),'DDEAF1' if ri==0 else ('F6F8FA' if ri%2==0 else 'FFFFFF')); tcPr.append(sh)
            for pp in cell.paragraphs:
                pp.paragraph_format.space_after=Pt(2); pp.paragraph_format.space_before=Pt(2)
                for r in pp.runs:
                    r.font.size=Pt(9); r.bold=(ri==0)
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Cm(w)
    doc.add_paragraph()
    return t
def fig(path, caption):
    r=doc.add_paragraph(); r.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r.add_run().add_picture(str(path),width=Cm(16.0))
    c=doc.add_paragraph(caption); c.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for run in c.runs: run.italic=True; run.font.size=Pt(9)

title=doc.add_paragraph(style='Title'); title.add_run('Báo cáo phần A phân hệ đóng học phí iBanking')
p('Môn học Kiến trúc hướng dịch vụ  |  Dự án giữa kỳ  |  Học kỳ 1 năm học 2026–2027')
p('Phạm vi người A: Account Service, Notification Service, giao diện web, thiết kế và kiểm thử phần A.')
p('Nhóm: ........................................    Thành viên A: ........................................')
p('Ngày cập nhật: 07/11/2026')
h('Tóm tắt')
p('Hệ thống mô phỏng việc người dùng iBanking đóng toàn bộ học phí cho mình hoặc cho sinh viên khác. Phần A đã có dịch vụ đăng nhập và hồ sơ, dịch vụ gửi email, giao diện web và Payment mock để phát triển độc lập. Dữ liệu số dư, học phí, giao dịch và OTP thuộc Payment Service của phần B. Gói A đã chạy trong Docker Compose với PostgreSQL; ba bài test tự động và frontend build thành công. Tích hợp Payment thật, email đến inbox và hai tình huống đồng thời cần được kiểm chứng trước khi nộp sản phẩm cuối.')

h('1 Giới thiệu và yêu cầu')
h('1.1 Phạm vi nghiệp vụ',2)
p('Người dùng đăng nhập bằng username và password; hệ thống hiển thị họ tên, số điện thoại, email, số dư và lịch sử giao dịch. Người dùng nhập MSSV để tra cứu tên sinh viên và số học phí. Khi khoản học phí chưa được thanh toán, số dư đủ và người dùng đồng ý điều khoản, hệ thống tạo giao dịch và gửi OTP tới email người nộp. Sau khi OTP hợp lệ, Payment Service cập nhật số dư, công nợ, lịch sử và gửi email xác nhận.')
h('1.2 Yêu cầu của phần A',2)
table(['Mã','Yêu cầu','Đầu ra'],[
('A1','Phân tích actor, chức năng, luồng chính và lỗi','Use Case Diagram và đặc tả'),
('A2','Mô tả service, dữ liệu và giao tiếp','Microservices Architecture Diagram'),
('A3','Đăng nhập và hồ sơ người nộp','Account Service, DB, migration, seed, JWT'),
('A4','Gửi OTP và xác nhận qua email','Notification Service, SMTP, messageId'),
('A5','Giao diện toàn luồng','React UI tích hợp API'),
('A6','Làm và kiểm thử độc lập','Payment mock và test A'),
('A7–A8','Đóng gói, báo cáo và slide','Source, Compose, README, tài liệu')], [1.6,7,7.2])
h('1.3 Tiêu chí đối chiếu rubric',2)
p('Phần A đóng góp trực tiếp vào Use Case Diagram, sơ đồ kiến trúc microservices, REST API, database/persistence của Account và Notification, đăng nhập, email OTP/xác nhận, giao diện và tài liệu triển khai. Transaction và concurrency của dữ liệu tài chính do B hiện thực; A phải chạy lại và trình bày bằng chứng sau khi ghép.')

h('2 Phân tích nghiệp vụ')
fig(uc,'Hình 1. Các chức năng và actor chính của phân hệ')
h('2.1 Luồng chính',2)
for s in ['Đăng nhập, nhận JWT và tải hồ sơ người nộp; thông tin này chỉ đọc.','Tự tra cứu khi MSSV đủ 8 chữ số; lấy tên sinh viên, mã khoản học phí và toàn bộ số tiền.','Kiểm tra số dư hiển thị, xem điều khoản và tạo giao dịch với requestId duy nhất.','Nhận OTP qua email người nộp, nhập mã để xác nhận; sau thành công đọc lại ví và lịch sử.']:
    bullet(s)
h('2.2 Luồng lỗi và điều kiện',2)
p('UI ngăn thao tác khi thiếu dữ liệu, khoản học phí đã trả, số dư hiển thị không đủ hoặc chưa đồng ý điều khoản. Backend vẫn phải kiểm tra lại vì dữ liệu có thể đổi trong lúc người dùng nhập OTP. Các lỗi gồm sai thông tin đăng nhập, MSSV không tồn tại, chưa có học phí, OTP sai/hết hạn và dịch vụ email không sẵn sàng. Khi đổi MSSV, giao diện xóa khoản học phí, giao dịch và OTP cũ; response tra cứu cũ không được ghi đè lựa chọn mới.')

h('3 Thiết kế kiến trúc')
fig(arch,'Hình 2. Kiến trúc các service và quyền sở hữu dữ liệu')
p('Account Service sở hữu người dùng và phát hành JWT. Payment Service của B sở hữu ví, sinh viên, công nợ, giao dịch và OTP; các thay đổi tài chính nằm trong cùng transaction PostgreSQL. Notification Service sở hữu trạng thái gửi email, nhận yêu cầu nội bộ từ Payment bằng X-Internal-Key và dùng SMTP. Trình duyệt chỉ gọi Account và Payment API. Khi A làm riêng, Payment mock chạy cổng 8089; khi ghép đổi sang Payment thật cổng 8082.')
table(['Service','Cổng','Dữ liệu sở hữu','API giao tiếp'],[
('Account','8081','users','Login, profile, health'),
('Payment B','8082','Ví, học phí, payment, OTP','Wallet, tuition, payments'),
('Notification','8083','email_messages','Gửi email nội bộ, health'),
('Payment mock','8089','Dữ liệu tạm trong RAM','Chỉ phục vụ UI A')],[3.0,1.6,5.8,5.4])

h('4 Database và dữ liệu mẫu của A')
h('4.1 Account Database',2)
p('Bảng users gồm id (khóa chính), username (duy nhất), password_hash, full_name, phone và email. Mật khẩu mẫu được băm Argon2 khi seed; ứng dụng không trả password_hash qua API. ID u1 và u2 dùng chung với bộ seed Payment của B.')
h('4.2 Notification Database',2)
p('Bảng email_messages gồm message_id (khóa chính), payload_hash, status và updated_at. Cùng messageId và cùng nội dung đã SENT trả kết quả cũ; cùng ID nhưng nội dung khác trả 409. Trạng thái FAILED cho phép thử lại. Migration được quản lý theo phiên bản bằng schema_migrations. SQLite phục vụ chạy local; cấu hình Compose dùng PostgreSQL với database riêng cho từng service.')
h('5 Thiết kế REST API phần A')
table(['Method','URI','Kết quả và lỗi chính'],[
('POST','/api/v1/auth/login','200 JWT; 400 validation; 401 sai thông tin'),
('GET','/api/v1/users/me','200 hồ sơ; 401 token thiếu hoặc sai'),
('POST','/internal/v1/notifications/email','200 SENT; 403 khóa sai; 409 gửi lặp đang xử lý/xung đột; 503 SMTP lỗi'),
('GET','/api/v1/health','200 UP và tên service')],[2.0,6.2,7.6])
p('Request và response dùng JSON UTF-8, tên trường lowerCamelCase. Model từ chối trường thừa; lỗi validation trả 400 với code VALIDATION_ERROR. JWT dùng HS256, kiểm tra chữ ký, issuer, audience và hạn dùng. API người dùng nhận Bearer token; API email nội bộ nhận X-Internal-Key. Khóa JWT, khóa nội bộ và thông tin SMTP không được đưa vào frontend.')
h('5.1 Mẫu request và response',2)
p('Login request: {"username":"demo1","password":"Demo!2026"}. Login response gồm accessToken, tokenType="Bearer", expiresIn=3600. Profile response gồm userId, fullName, phone, email. Email request gồm messageId, type (OTP hoặc PAYMENT_SUCCESS), to và data tương ứng. Response email gồm messageId và status="SENT".')

h('6 Hiện thực giao diện và email')
p('Frontend React gồm màn hình đăng nhập, hồ sơ và số dư chỉ đọc, tra cứu học phí, điều khoản, tạo thanh toán toàn bộ, nhập OTP, kết quả và lịch sử. Khi MSSV đủ 8 chữ số, frontend tự gọi API; request cũ bị hủy và số thứ tự request ngăn phản hồi chậm ghi đè dữ liệu mới. Sau confirm thành công, frontend đọc lại wallet và history từ server thay vì tự trừ tiền trên trình duyệt.')
p('Notification Service xây dựng hai mẫu email: OTP gắn paymentId và thời hạn; email xác nhận gồm giao dịch, sinh viên, số tiền và thời gian. Dịch vụ ghi messageId cùng hash nội dung để xử lý gọi lặp. Lỗi SMTP trả NOTIFICATION_UNAVAILABLE; việc provider chấp nhận gửi không đồng nghĩa email chắc chắn tới inbox, vì vậy cần kiểm tra hộp thư khi demo thật.')

h('7 Kiểm thử và bằng chứng hiện tại')
table(['Hạng mục','Kết quả đã chạy','Giới hạn'],[
('Pytest phần A','3 passed','Test API, provider mô phỏng và Payment mock'),
('Frontend build','Thành công','Chưa thay cho kiểm thử thao tác trình duyệt'),
('Migration và seed','PostgreSQL trong Compose; 2 users có hash Argon2','Chưa chạy Payment DB của B'),
('Luồng API với mock','Login 200; create 201; OTP sai 422; confirm 200; ví 10 triệu còn 3 triệu','Không chứng minh email và transaction thật'),
('Docker Compose','5 container chạy; 4 HTTP endpoint trả 200','Payment hiện vẫn là mock')],[3.5,5.5,6.8])
p('Trong Compose, login trả 200, tạo payment 201, OTP sai 422, OTP mock đúng 200; số dư mock từ 10 triệu còn 3 triệu. Payment mock đã được restart để trả dữ liệu demo về ban đầu. Account DB có 2 user và hash Argon2; restart Account/Notification xong Account vẫn trả 200. Notification trả 403 khi thiếu khóa; khi SMTP chưa cấu hình, yêu cầu hợp lệ trả 503 và lưu FAILED. Các case T01/T02/T34 mới được kiểm tra một phần; không đánh dấu toàn bộ 37 case là PASS. T35 yêu cầu UI, Payment và email thật. T21/T22 yêu cầu đối chiếu dữ liệu tài chính do B xử lý.')

h('8 Triển khai và tích hợp')
p('Chạy local: cài requirements-A.txt, chạy seed Account và init database Notification, rồi khởi chạy uvicorn tại 8081/8083, Payment mock 8089 và Vite 5173. File compose-A.yaml cấu hình PostgreSQL, Account, Notification, mock và frontend. Khi ghép Payment thật, đổi VITE_PAYMENT_API_BASE_URL sang http://localhost:8082/api/v1; Payment gọi Notification bằng hostname notification trong Compose. Đồng bộ JWT_SECRET, issuer, audience và INTERNAL_API_KEY giữa các service; cấu hình SMTP và email thử do nhóm kiểm soát.')
h('8.1 Việc phải nghiệm thu trước khi nộp',2)
for s in ['Thử cài lại từ môi trường sạch hoặc máy khác theo README.','Ghép Payment Service B; tắt mock trong luồng demo.','Nhận OTP và email thành công trong hộp thư thật; chụp ảnh màn hình và ghi kết quả.','Chạy ca đổi MSSV nhanh trên trình duyệt và hai bài concurrency T21, T22; lưu dữ liệu trước/sau.','Cập nhật sơ đồ, báo cáo, slide theo code và kết quả tích hợp cuối cùng.']:
    bullet(s)

h('9 Kết luận và đóng góp')
p('Phần A đã có source chạy local cho Account, Notification, frontend và mock; có migration, seed, hướng dẫn, sơ đồ nguồn và kiểm thử cơ bản. Trạng thái hiện tại là bản triển khai để ghép, chưa phải kết quả nghiệm thu cuối. Người A chịu trách nhiệm hoàn tất kiểm thử UI, email thật, tài liệu và xác minh lại hai tình huống đồng thời sau khi B bàn giao Payment Service.')
h('Tài liệu tham khảo')
p('1. Đề dự án giữa kỳ Phân hệ đóng học phí của ứng dụng iBanking, 3 trang do giảng viên cung cấp.')
p('2. Phiếu chấm điểm giữa kỳ môn Kiến trúc hướng dịch vụ, rubric-midterm.pdf, 3 trang.')
p('3. Bộ chốt phân công và hợp đồng dự án iBanking phiên bản 1.0.0; OpenAPI, dữ liệu mẫu và ma trận kiểm thử do nhóm sử dụng.')

footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
footer.add_run('Báo cáo phần A  |  iBanking')
doc.save(OUT)
print(OUT)
