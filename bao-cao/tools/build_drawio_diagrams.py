"""Editable project diagrams based on contract 1.0.0 and the implemented A services."""
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'ibanking-so-do-day-du.drawio'

mx = ET.Element('mxfile', {'host':'drawio','version':'26.0.0','type':'device'})

STYLES = {
    'title':'text;html=1;align=left;verticalAlign=middle;fontStyle=1;fontSize=24;fontColor=#173045;strokeColor=none;fillColor=none;',
    'note':'text;html=1;align=left;verticalAlign=middle;fontSize=13;fontColor=#526575;strokeColor=none;fillColor=none;whiteSpace=wrap;',
    'actor':'shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;fontSize=14;fontColor=#173045;',
    'use':'ellipse;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=15;fillColor=#E7F2F8;strokeColor=#48758B;strokeWidth=2;',
    'service':'rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=16;fontStyle=1;fillColor=#DDEEF7;strokeColor=#3C7997;strokeWidth=2;',
    'data':'shape=cylinder3;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=14;fillColor=#E3F1E2;strokeColor=#6A9A67;strokeWidth=2;',
    'external':'rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=15;fillColor=#F3F3F3;strokeColor=#888888;dashed=1;',
    'client':'rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=16;fillColor=#E9E3F3;strokeColor=#8970A7;strokeWidth=2;',
    'table':'swimlane;startSize=30;horizontal=1;rounded=0;whiteSpace=wrap;html=1;align=center;verticalAlign=top;fontSize=15;fontStyle=1;fillColor=#DDEAF1;strokeColor=#50738A;strokeWidth=2;container=1;collapsible=0;',
    'fields':'text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=13;fontColor=#203B4A;strokeColor=none;fillColor=none;spacingLeft=12;spacingTop=6;',
    'process':'rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=15;fillColor=#DDEEF7;strokeColor=#3C7997;strokeWidth=2;',
    'decision':'rhombus;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=14;fillColor=#FFF1C9;strokeColor=#B58E34;strokeWidth=2;',
    'terminal':'ellipse;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=15;fillColor=#E1F1DF;strokeColor=#699A65;strokeWidth=2;',
    'error':'rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=14;fillColor=#FAE0DE;strokeColor=#C4756F;strokeWidth=2;',
    'lane':'swimlane;startSize=32;horizontal=1;rounded=0;html=1;align=left;verticalAlign=top;fontSize=16;fontStyle=1;fillColor=#F7FAFC;strokeColor=#B8CBD4;container=1;collapsible=0;',
}
EDGE='edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;endSize=8;strokeColor=#506B7A;strokeWidth=2;fontSize=13;labelBackgroundColor=#FFFFFF;'

def page(name, width=1600, height=1000):
    d = ET.SubElement(mx,'diagram',{'name':name,'id':name.lower().replace(' ','-')})
    model=ET.SubElement(d,'mxGraphModel',{'dx':'1600','dy':'1000','grid':'1','gridSize':'10','guides':'1','tooltips':'1','connect':'1','arrows':'1','fold':'1','page':'1','pageScale':'1','pageWidth':str(width),'pageHeight':str(height),'math':'0','shadow':'0'})
    root=ET.SubElement(model,'root')
    ET.SubElement(root,'mxCell',{'id':'0'}); ET.SubElement(root,'mxCell',{'id':'1','parent':'0'})
    return root

def node(root,id,label,x,y,w,h,kind='service',parent='1',style=None):
    c=ET.SubElement(root,'mxCell',{'id':id,'value':label.replace('&#xa;','\n'),'style':style or STYLES[kind],'vertex':'1','parent':parent})
    ET.SubElement(c,'mxGeometry',{'x':str(x),'y':str(y),'width':str(w),'height':str(h),'as':'geometry'})
    return c

def edge(root,id,src,dst,label='',style=None,points=None):
    c=ET.SubElement(root,'mxCell',{'id':id,'value':label,'style':style or EDGE,'edge':'1','parent':'1','source':src,'target':dst})
    g=ET.SubElement(c,'mxGeometry',{'relative':'1','as':'geometry'})
    if points:
        a=ET.SubElement(g,'Array',{'as':'points'})
        for x,y in points: ET.SubElement(a,'mxPoint',{'x':str(x),'y':str(y)})
    return c

def entity(root,id,label,fields,x,y,w=270,h=185):
    node(root,id,label,x,y,w,h,'table')
    node(root,id+'_fields','&#xa;'.join(fields),10,35,w-20,h-45,'fields',parent=id)

# 1. Use Case Diagram
r=page('01 Use Case',1700,1000)
node(r,'uc_title','USE CASE  |  PHÂN HỆ ĐÓNG HỌC PHÍ IBANKING',40,20,1250,50,'title')
node(r,'uc_note','Actor chính: người nộp tiền. Email provider là hệ thống ngoài. Luồng thanh toán toàn bộ, không có đăng ký tài khoản.',40,75,1450,35,'note')
node(r,'payer','Người nộp tiền',90,390,70,110,'actor')
node(r,'email_provider','Email provider',1510,390,70,110,'actor')
node(r,'system','Hệ thống iBanking',280,150,1170,710,'lane')
uc_nodes=[('login','Đăng nhập',360,220),('profile','Xem hồ sơ và số dư',780,220),('lookup','Tra cứu học phí',360,390),('create','Tạo giao dịch thanh toán',780,390),('confirm','Xác thực OTP',360,560),('history','Xem kết quả và lịch sử',780,560),('mail','Gửi OTP và email xác nhận',780,730)]
for id,label,x,y in uc_nodes: node(r,id,label,x-280,y-150,320,90,'use',parent='system')
for id,target in [('a1','login'),('a2','profile'),('a3','lookup'),('a4','create'),('a5','confirm'),('a6','history')]:
    edge(r,id,'payer',target,'',EDGE.replace('endArrow=block;endFill=1;','endArrow=none;'))
edge(r,'a7','email_provider','mail','',EDGE.replace('endArrow=block;endFill=1;','endArrow=none;'))
edge(r,'inc1','create','lookup','«include»',EDGE+'dashed=1;endArrow=open;')
edge(r,'inc2','create','mail','«include»',EDGE+'dashed=1;endArrow=open;')
edge(r,'inc3','confirm','mail','«include»',EDGE+'dashed=1;endArrow=open;')

# 2. Architecture Diagram
r=page('02 Architecture',1700,1000)
node(r,'ar_title','KIẾN TRÚC MICROSERVICES  |  HỢP ĐỒNG NHÓM 1.0.0',40,20,1450,50,'title')
node(r,'ar_note','Account và Notification đã hiện thực trong gói A. Payment B là service tài chính theo hợp đồng; sơ đồ cần cập nhật theo code B khi ghép.',40,75,1550,40,'note')
node(r,'browser','Người nộp&#xa;trình duyệt',60,380,230,90,'client')
node(r,'frontend','React UI&#xa;localhost:5173',370,380,250,90,'client')
node(r,'account','Account Service&#xa;FastAPI :8081',800,170,290,100,'service')
node(r,'payment','Payment Service B&#xa;FastAPI :8082',800,390,290,100,'service')
node(r,'notification','Notification Service&#xa;FastAPI :8083',800,650,290,100,'service')
node(r,'acc_db','Account DB&#xa;users',1240,170,270,100,'data')
node(r,'pay_db','Payment DB&#xa;wallets · students · tuitions&#xa;payments · OTP · email jobs',1240,390,270,120,'data')
node(r,'not_db','Notification DB&#xa;email_messages',1240,650,270,100,'data')
node(r,'smtp','SMTP provider',1240,820,270,80,'external')
edge(r,'ar1','browser','frontend','HTTPS')
edge(r,'ar2','frontend','account','REST + JWT')
edge(r,'ar3','frontend','payment','REST + JWT')
edge(r,'ar4','account','acc_db','SQL')
edge(r,'ar5','payment','pay_db','1 DB transaction')
edge(r,'ar6','payment','notification','REST + X-Internal-Key')
edge(r,'ar7','notification','not_db','messageId')
edge(r,'ar8','notification','smtp','SMTP')
node(r,'ar_legend','Xanh lam: ứng dụng/service     Xanh lục: database     Xám: hệ thống ngoài',50,900,950,40,'note')

# 3. ERD, with actual A schema and proposed B schema
r=page('03 ERD',1800,1180)
node(r,'er_title','ERD  |  DỮ LIỆU PHỤC VỤ THANH TOÁN HỌC PHÍ',40,20,1550,50,'title')
node(r,'er_note','Account/Notification: bảng đã hiện thực. Payment B: mô hình logic theo hợp đồng, cần đồng bộ tên cột và khóa với migration B khi nhận source.',40,75,1650,50,'note')
entity(r,'users','users  [Account DB]',['PK id','UQ username','password_hash','full_name','phone','email'],50,170,280,210)
entity(r,'wallets','wallets  [Payment DB]',['PK user_id','balance >= 0','currency'],420,170,280,180)
entity(r,'students','students  [Payment DB]',['PK student_id (MSSV)','student_name'],790,170,280,160)
entity(r,'messages','email_messages  [Notification DB]',['PK message_id','payload_hash','status','updated_at'],1200,170,350,190)
entity(r,'otps','otp_challenges  [Payment DB]',['PK otp_id','FK payment_id','code_hash','expires_at','used_at'],50,610,300,210)
entity(r,'payments','payments  [Payment DB]',['PK payment_id','user_id (cross-service ref)','FK tuition_id','request_id (UQ with user_id)','amount · status · timestamps'],420,560,320,260)
entity(r,'tuitions','tuitions  [Payment DB]',['PK tuition_id','FK student_id','amount > 0','status · paid_at'],820,560,280,210)
entity(r,'jobs','email_jobs  [Payment DB]',['PK job_id','FK payment_id','message_id','type · status · retry_at'],1240,590,300,210)
edge(r,'er1','users','wallets','1 : 1  user_id',EDGE+'dashed=1;')
edge(r,'er2','users','payments','1 : N  user_id',EDGE+'dashed=1;exitX=1;exitY=1;entryX=0;entryY=0;',[(360,420),(370,520)])
edge(r,'er3','wallets','payments','1 : N')
edge(r,'er4','students','tuitions','1 : N')
edge(r,'er5','tuitions','payments','1 : N')
edge(r,'er6','payments','otps','1 : 1')
edge(r,'er7','payments','jobs','1 : N','edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;endSize=8;strokeColor=#506B7A;strokeWidth=2;fontSize=13;labelBackgroundColor=#FFFFFF;exitX=0.5;exitY=1;entryX=0.5;entryY=1;',[(580,920),(1390,920)])
edge(r,'er8','jobs','messages','messageId (API, no FK)',EDGE+'dashed=1;')
node(r,'er_legend','Nét đứt: tham chiếu qua service/API, không tạo foreign key giữa database. Ràng buộc một SUCCESS cho mỗi tuition_id cần có ở Payment DB.',50,1030,1590,60,'note')

# 4. Payment and OTP workflow
r=page('04 Payment Flow',1700,1150)
node(r,'pf_title','LUỒNG THANH TOÁN VÀ XÁC THỰC OTP',40,20,1500,50,'title')
node(r,'pf_note','Mô tả nghiệp vụ theo hợp đồng. Payment B cần chứng minh cập nhật tài chính nguyên tử trong transaction.',40,75,1550,40,'note')
flow=[('start','Đăng nhập',80,190,'terminal'),('lookup2','Tra cứu MSSV',330,190,'process'),('eligible','UNPAID và đủ số dư?',620,170,'decision'),('create2','Tạo payment&#xa;PENDING_OTP',970,190,'process'),('mailotp','Gửi OTP email&#xa;TTL 5 phút',1270,190,'process'),('enter','Nhập OTP',1270,460,'process'),('check','OTP hợp lệ?',970,450,'decision'),('lock','Khóa ví + học phí&#xa;kiểm tra lại',620,460,'process'),('commit','Cùng transaction: trừ tiền&#xa;gạch nợ · lịch sử · OTP',300,460,'process'),('success','SUCCESS + email xác nhận',80,480,'terminal'),('reject','Từ chối, không trừ tiền',620,790,'error'),('otp_error','OTP sai/hết hạn',970,790,'error')]
for id,label,x,y,kind in flow: node(r,id,label,x,y,220 if kind!='decision' else 240,90 if kind!='decision' else 130,kind)
for id,a,b,label in [('p1','start','lookup2',''),('p2','lookup2','eligible',''),('p3','eligible','create2','Có'),('p4','create2','mailotp',''),('p5','mailotp','enter',''),('p6','enter','check',''),('p7','check','lock','Đúng'),('p8','lock','commit','Hợp lệ'),('p9','commit','success','Commit'),('p10','eligible','reject','Không'),('p11','check','otp_error','Sai/hết hạn'),('p12','lock','reject','Thiếu tiền/đã đóng')]: edge(r,id,a,b,label)
node(r,'pf_foot','Create chỉ kiểm tra sơ bộ; confirm phải kiểm tra lại sau khi chờ OTP. Email thành công gửi sau commit qua email job. Lỗi kỹ thuật trong transaction phải rollback toàn bộ.',70,980,1500,70,'note')

# 5. Concurrency and consistency
r=page('05 Concurrency',1700,1050)
node(r,'co_title','HAI TÌNH HUỐNG CONCURRENCY BẮT BUỘC',40,20,1480,50,'title')
node(r,'co_note','Thiết kế kiểm soát thuộc Payment B. Người A chạy lại kịch bản và đối chiếu UI, API, database sau khi tích hợp.',40,75,1550,40,'note')
node(r,'case1','T21  |  CÙNG VÍ 10 TRIỆU',70,160,1500,45,'title')
node(r,'w1','Giao dịch A&#xa;HP001: 7 triệu',90,250,260,100,'process')
node(r,'w2','Giao dịch B&#xa;HP002: 7 triệu',90,440,260,100,'process')
node(r,'walletlock','Khóa hàng wallet&#xa;và kiểm tra balance',530,330,330,120,'decision')
node(r,'onewin','Một giao dịch SUCCESS&#xa;ví còn 3 triệu',1080,250,360,100,'terminal')
node(r,'onelose','Giao dịch còn lại FAILED&#xa;không chi vượt số dư',1080,440,360,100,'error')
edge(r,'c1','w1','walletlock','confirm')
edge(r,'c2','w2','walletlock','confirm')
edge(r,'c3','walletlock','onewin','đủ tiền')
edge(r,'c4','walletlock','onelose','thiếu tiền')
node(r,'case2','T22  |  HAI TÀI KHOẢN, CÙNG KHOẢN HP001',70,625,1500,45,'title')
node(r,'u1','u1 thanh toán HP001',90,730,290,90,'process')
node(r,'u2','u2 thanh toán HP001',90,870,290,90,'process')
node(r,'tuitionlock','Khóa hàng tuition HP001&#xa;và kiểm tra UNPAID',570,770,330,120,'decision')
node(r,'paid','Một payment SUCCESS&#xa;HP001 chuyển PAID',1110,710,350,90,'terminal')
node(r,'duplicate','Payment còn lại FAILED&#xa;ví không bị trừ',1110,870,350,90,'error')
edge(r,'c5','u1','tuitionlock','confirm')
edge(r,'c6','u2','tuitionlock','confirm')
edge(r,'c7','tuitionlock','paid','thắng khóa')
edge(r,'c8','tuitionlock','duplicate','đã PAID')

ET.indent(mx,space='  ')
OUT.write_bytes(ET.tostring(mx,encoding='utf-8',xml_declaration=True))
names=['01-use-case','02-microservices-architecture','03-erd','04-payment-otp-flow','05-concurrency']
for diagram,stem in zip(mx.findall('diagram'),names):
    single=ET.Element('mxfile',{'host':'drawio','version':'26.0.0','type':'device'})
    single.append(ET.fromstring(ET.tostring(diagram,encoding='utf-8')))
    ET.indent(single,space='  ')
    (OUT.parent/(stem+'.drawio')).write_bytes(ET.tostring(single,encoding='utf-8',xml_declaration=True))
print(OUT)
