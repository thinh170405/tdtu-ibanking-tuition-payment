from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
TMP=ROOT/'tmp'/'docx'
TMP.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'A1-phan-tich-nghiep-vu-ibanking.docx'
FONT='C:/Windows/Fonts/arial.ttf'

im=Image.new('RGB',(1500,900),'white'); d=ImageDraw.Draw(im)
f=ImageFont.truetype(FONT,27); small=ImageFont.truetype(FONT,20)
d.rounded_rectangle((315,45,1320,840),radius=15,outline='#36596B',width=4)
d.text((620,60),'Phân hệ đóng học phí iBanking',font=f,fill='#173045')
# Actors
d.ellipse((85,260,145,320),outline='#173045',width=4)
d.line((115,320,115,440),fill='#173045',width=4)
d.line((55,355,175,355),fill='#173045',width=4)
d.line((115,440,60,505),fill='#173045',width=4)
d.line((115,440,170,505),fill='#173045',width=4)
d.text((25,520),'Người nộp tiền',font=f,fill='#173045')
d.ellipse((1380,330,1440,390),outline='#173045',width=4)
d.line((1410,390,1410,490),fill='#173045',width=4)
d.line((1355,420,1465,420),fill='#173045',width=4)
d.line((1410,490,1360,550),fill='#173045',width=4)
d.line((1410,490,1460,550),fill='#173045',width=4)
d.text((1325,570),'Email provider',font=small,fill='#173045')
uses=[('UC01 Đăng nhập',(400,140,740,225)),('UC02 Xem hồ sơ và số dư',(790,140,1250,225)),('UC03 Tra cứu học phí',(400,290,740,375)),('UC04 Tạo giao dịch',(790,290,1250,375)),('UC05 Xác thực OTP',(400,460,740,545)),('UC06 Xem kết quả và lịch sử',(790,460,1250,545)),('Gửi email OTP và xác nhận',(785,660,1255,745))]
for label,box in uses:
    d.ellipse(box,fill='#EDF5F9',outline='#3B647B',width=3)
    bb=d.textbbox((0,0),label,font=small)
    d.text(((box[0]+box[2]-bb[2])/2,(box[1]+box[3]-bb[3])/2),label,font=small,fill='#173045')
for dest in [(400,180),(400,330),(400,500),(790,180),(790,330),(790,500)]:
    d.line((175,390,*dest),fill='#6B8491',width=2)
d.line((1250,702,1355,440),fill='#6B8491',width=2)
d.line((1020,375,1020,660),fill='#6B8491',width=2)
d.line((740,500,785,702),fill='#6B8491',width=2)
FIG=TMP/'a1-use-case.png'; im.save(FIG)

doc=Document(); sec=doc.sections[0]
sec.top_margin=Cm(2.1); sec.bottom_margin=Cm(1.9); sec.left_margin=Cm(2.2); sec.right_margin=Cm(2.1)
for name in ['Normal','Title','Heading 1','Heading 2']:
    st=doc.styles[name]; st.font.name='Arial'; st.font.color.rgb=RGBColor(0,0,0)
doc.styles['Normal'].font.size=Pt(10.5); doc.styles['Normal'].paragraph_format.space_after=Pt(6)
for name,size in [('Title',20),('Heading 1',13),('Heading 2',11)]:
    st=doc.styles[name]; st.font.size=Pt(size); st.font.bold=True
    st.paragraph_format.space_before=Pt(12); st.paragraph_format.space_after=Pt(7)
ppr=doc.styles['Title']._element.get_or_add_pPr()
for x in ppr.findall(qn('w:pBdr')): ppr.remove(x)

def para(s='',style=None): return doc.add_paragraph(s,style)
def head(s,level=1): doc.add_heading(s,level)
def tbl(headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers)); t.style='Table Grid'
    for i,h in enumerate(headers): t.rows[0].cells[i].text=h
    for row in rows:
        cells=t.add_row().cells
        for i,x in enumerate(row):cells[i].text=str(x)
    for j,row in enumerate(t.rows):
        for cell in row.cells:
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'DDEAF1' if j==0 else ('F7F9FA' if j%2==0 else 'FFFFFF'))
            cell._tc.get_or_add_tcPr().append(sh)
            for pp in cell.paragraphs:
                pp.paragraph_format.space_before=Pt(2);pp.paragraph_format.space_after=Pt(2)
                if j < len(t.rows)-1: pp.paragraph_format.keep_with_next=True
                for run in pp.runs:run.font.size=Pt(9);run.bold=(j==0)
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths):row.cells[i].width=Cm(w)
    doc.add_paragraph()
def spec(code,title,actor,pre,main,errors,post):
    head(code+' '+title,2)
    tbl(['Mục','Đặc tả'],[('Actor',actor),('Điều kiện trước',pre),('Luồng chính','\n'.join(f'{i}. {s}' for i,s in enumerate(main,1))),('Luồng lỗi / ngoại lệ','\n'.join(f'{i}. {s}' for i,s in enumerate(errors,1))),('Điều kiện sau',post)],[3.2,12.6])

doc.add_paragraph('A1 Phân tích nghiệp vụ phân hệ đóng học phí iBanking',style='Title')
para('Dự án giữa kỳ môn Kiến trúc hướng dịch vụ  |  Phần việc người A')
para('Nhóm: ........................................    Người A: ........................................')
para('Ngày cập nhật: 03/11/2026')
head('Mục tiêu và phạm vi')
para('Tài liệu mô tả actor, các chức năng chính, điều kiện trước/sau, luồng chuẩn và luồng lỗi của phân hệ đóng học phí. Người dùng có thể đóng học phí toàn bộ cho chính mình hoặc sinh viên khác bằng tài khoản đang đăng nhập. Phần A đặc tả nghiệp vụ và giao diện; Payment Service của người B thực hiện cập nhật tài chính và kiểm soát đồng thời.')
head('1 Quy tắc nghiệp vụ')
tbl(['Mã','Quy tắc'],[
('R01','Người dùng phải đăng nhập bằng username và password; không có chức năng đăng ký.'),
('R02','Họ tên, điện thoại, email và số dư của người nộp lấy từ tài khoản đăng nhập, không cho sửa trên màn hình thanh toán.'),
('R03','Tra cứu học phí bằng MSSV. Thanh toán toàn bộ khoản học phí; không thanh toán một phần.'),
('R04','Chỉ tạo giao dịch khi khoản học phí chưa thanh toán, số dư đủ và người dùng đồng ý điều khoản.'),
('R05','OTP gắn với một giao dịch, gửi đến email người nộp, có hiệu lực 5 phút và dùng thành công một lần.'),
('R06','Sau xác thực thành công: kiểm tra lại điều kiện, trừ tiền, gạch nợ học phí, lưu lịch sử và gửi email xác nhận.'),
('R07','Nhiều yêu cầu đồng thời không được chi vượt số dư hoặc thanh toán thành công hai lần cho cùng khoản học phí.')],[2.0,13.8])
head('2 Actor và Use Case Diagram')
tbl(['Actor','Vai trò'],[('Người nộp tiền','Đăng nhập, tra cứu MSSV, xác nhận thanh toán, nhập OTP và xem kết quả/lịch sử.'),('Email provider','Nhận yêu cầu gửi OTP và email xác nhận từ Notification Service.')],[3.7,12.1])
q=doc.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER;q.add_run().add_picture(str(FIG),width=Cm(16.2))
q=doc.add_paragraph('Hình 1. Use Case Diagram của phân hệ đóng học phí');q.alignment=WD_ALIGN_PARAGRAPH.CENTER
for r in q.runs:r.font.italic=True;r.font.size=Pt(9)
para('File nguồn sơ đồ để chỉnh sửa: docs/use-case-A.puml. UC04 dùng kết quả tra cứu UC03; UC05 xác nhận giao dịch UC04. Hệ thống email là dịch vụ ngoài được gọi để gửi OTP và thông báo thành công.')
head('3 Đặc tả các Use Case')
spec('UC01','Đăng nhập','Người nộp tiền','Có tài khoản mẫu đã lưu; chưa cần đăng nhập.',
['Nhập username và password.','Account Service kiểm tra thông tin; nếu đúng phát JWT.','Giao diện tải hồ sơ, số dư và lịch sử của tài khoản.'],
['Thiếu/sai kiểu trường: 400 VALIDATION_ERROR.','Sai username hoặc password: 401 INVALID_CREDENTIALS.','Token hết hạn hoặc không hợp lệ khi gọi API: 401 UNAUTHORIZED.'],
'Người dùng có JWT hợp lệ, xem được các chức năng thanh toán; sai thông tin thì không có phiên đăng nhập.')
spec('UC02','Xem thông tin người nộp','Người nộp tiền','Đã đăng nhập bằng JWT hợp lệ.',
['Giao diện gọi Account /users/me và Payment /wallet.','Hiển thị họ tên, điện thoại, email và số dư.','Các trường của người nộp ở màn hình thanh toán chỉ đọc.'],
['JWT thiếu/sai/hết hạn: 401 UNAUTHORIZED.','Ví chưa tồn tại: 404 WALLET_NOT_FOUND.','Một API không sẵn sàng: hiển thị lỗi, không cho tạo giao dịch.'],
'Thông tin người nộp hiển thị đúng theo tài khoản; không có thay đổi hồ sơ hoặc số dư ở bước này.')
spec('UC03','Tra cứu học phí','Người nộp tiền','Đã đăng nhập; nhập MSSV gồm 8 chữ số.',
['Khi MSSV đủ 8 chữ số, giao diện tự gọi Payment /tuition/{mssv}.','Hiển thị họ tên sinh viên, MSSV, mã học phí, số tiền và trạng thái.','Nếu đổi MSSV, xóa kết quả cũ và bỏ phản hồi chậm của lần tra cứu trước.'],
['MSSV sai định dạng: 400 VALIDATION_ERROR.','Không có sinh viên: 404 STUDENT_NOT_FOUND.','Có sinh viên nhưng chưa có khoản học phí: 404 TUITION_NOT_FOUND.','Khoản đã PAID: vẫn hiển thị nhưng không cho thanh toán.'],
'Người dùng thấy đúng khoản học phí của MSSV hiện tại; chưa phát sinh giao dịch hoặc trừ tiền.')
spec('UC04','Tạo giao dịch thanh toán','Người nộp tiền','Đã đăng nhập; có khoản UNPAID; số dư hiển thị đủ; đã đồng ý điều khoản.',
['Giao diện gửi tuitionId, termsAccepted=true và requestId duy nhất.','Payment kiểm tra lại học phí và số dư, lấy số tiền từ server.','Payment tạo giao dịch PENDING_OTP, phát OTP hạn 5 phút và yêu cầu gửi tới email người nộp.'],
['Thiếu điều khoản/requestId sai: 400 VALIDATION_ERROR.','Học phí đã đóng: 409 TUITION_ALREADY_PAID.','Số dư không đủ: 422 INSUFFICIENT_BALANCE.','Email OTP không gửi được: 503 NOTIFICATION_UNAVAILABLE.','Gọi lặp cùng requestId: trả lại giao dịch cũ; cùng ID khác nội dung: 409 REQUEST_ID_CONFLICT.'],
'Giao dịch chờ OTP; chưa trừ tiền. OTP được gửi tới email người nộp nếu tạo thành công.')
spec('UC05','Xác thực OTP và thực hiện thanh toán','Người nộp tiền','Có giao dịch PENDING_OTP của chính người dùng; OTP đã gửi.',
['Người dùng nhập mã OTP 6 chữ số.','Payment kiểm tra chủ giao dịch, mã OTP và thời hạn; kiểm tra lại số dư và trạng thái học phí.','Nếu hợp lệ, Payment cập nhật số dư, học phí, lịch sử, trạng thái giao dịch và tiêu thụ OTP trong transaction.','Notification gửi email xác nhận sau khi giao dịch thành công.'],
['OTP sai: 422 INVALID_OTP; chưa trừ tiền.','OTP hết hạn: 422 OTP_EXPIRED; không cho dùng lại.','Học phí đã được trả bởi giao dịch khác: 409 TUITION_ALREADY_PAID.','Số dư đã thay đổi thành thiếu: 422 INSUFFICIENT_BALANCE.','Lỗi kỹ thuật trong transaction: rollback toàn bộ; không để trừ tiền dở dang.'],
'Thành công: payment SUCCESS, số dư giảm đúng một lần, học phí PAID, có lịch sử; thất bại: không trừ tiền cho giao dịch đó.')
spec('UC06','Xem kết quả và lịch sử','Người nộp tiền','Đã đăng nhập; có thể có hoặc chưa có giao dịch.',
['Sau confirm, giao diện hiển thị trạng thái giao dịch.','Giao diện đọc lại wallet và danh sách payments từ Payment Service.','Chỉ hiển thị giao dịch thuộc người dùng hiện tại, gồm pending/success/failed/expired.'],
['JWT thiếu/sai: 401 UNAUTHORIZED.','Payment không thuộc người dùng hoặc không tồn tại: 404 PAYMENT_NOT_FOUND.','API tạm thời không sẵn sàng: hiển thị lỗi và cho phép tải lại.'],
'Người dùng xem được số dư và lịch sử phản ánh dữ liệu cuối cùng từ server.')
head('4 Các tình huống đồng thời cần bảo vệ')
para('T21: Ví 10 triệu đồng thời trả hai khoản học phí mỗi khoản 7 triệu. Chỉ một giao dịch thành công; ví còn 3 triệu và chỉ một khoản được đóng. T22: Hai tài khoản cùng trả HP001. Chỉ một giao dịch thành công và chỉ ví thắng bị trừ. Đây là yêu cầu nghiệp vụ chung; người B hiện thực, người A chạy lại và kiểm tra giao diện/dữ liệu sau khi ghép.')
head('5 Truy vết sang giao diện và kiểm thử')
tbl(['Use Case','Màn hình hoặc API','Kiểm thử cần có'],[
('UC01','Login; Account /auth/login','Đúng/sai mật khẩu, JWT sai/hết hạn'),
('UC02','Hồ sơ và số dư; /users/me, /wallet','Thông tin chỉ đọc, đúng user'),
('UC03','Ô MSSV; /tuition/{mssv}','Tự tra cứu, MSSV đổi nhanh, chưa có/đã đóng'),
('UC04','Điều khoản và nút xác nhận; POST /payments','Thiếu tiền, đã đóng, requestId lặp'),
('UC05','Màn hình OTP; POST /payments/{id}/confirm','OTP sai/hết hạn, thành công, rollback'),
('UC06','Kết quả và lịch sử; GET /payments','Số dư cập nhật, chỉ xem dữ liệu của mình')],[2.3,6.4,7.1])
head('Tài liệu đối chiếu')
para('Đề dự án giữa kỳ Phân hệ đóng học phí của ứng dụng iBanking; rubric-midterm.pdf; bộ chốt phân công và hợp đồng dự án phiên bản 1.0.0 gồm OpenAPI, dữ liệu mẫu và ma trận kiểm thử.')
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER;footer.add_run('A1 Phân tích nghiệp vụ  |  iBanking')
doc.save(OUT);print(OUT)
