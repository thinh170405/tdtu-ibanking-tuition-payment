"""Build the complete midterm report from reviewed Markdown sections."""
import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = ROOT / "bao-cao-giua-ky-ibanking-day-du.docx"
SOURCES = [DOCS / "01-phan-tich-nghiep-vu-uml.md", DOCS / "02-kien-truc-microservices-va-rest-api.md", DOCS / "04-08-hien-thuc-kiem-thu-trien-khai.md"]
FIGURES = {
    "1.4.": (DOCS / "previews" / "01-use-case-final.png", "Hình 1. Use Case Diagram của phân hệ đóng học phí"),
    "1.5.": (DOCS / "previews" / "03-conceptual-erd-final.png", "Hình 2. ERD khái niệm với năm thực thể cốt lõi"),
    "2.3.": (DOCS / "previews" / "02-microservices-architecture-final.png", "Hình 3. Microservices Architecture Diagram của hệ thống tích hợp"),
    "4.1.": (DOCS / "previews" / "04-physical-erd-final.png", "Hình 4. ERD vật lý của tám bảng trong ba database"),
    "5.2.": (DOCS / "previews" / "05-payment-otp-flow-final.png", "Hình 5. Luồng thanh toán, OTP và transaction"),
    "6.": (DOCS / "previews" / "06-concurrency-final.png", "Hình 6. Xử lý hai tình huống giao dịch đồng thời"),
}


def clean(value):
    value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
    return value.replace("**", "").replace("`", "").replace("*", "")


doc = Document()
section = doc.sections[0]
section.top_margin = Cm(2.15)
section.bottom_margin = Cm(2.0)
section.left_margin = Cm(2.4)
section.right_margin = Cm(2.2)
styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Arial"
normal.font.size = Pt(10.25)
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.1
for name, size, before, after in [("Title", 21, 0, 12), ("Heading 1", 15, 18, 8), ("Heading 2", 12, 12, 6), ("Heading 3", 10.5, 9, 4)]:
    st = styles[name]
    st.font.name = "Arial"
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.paragraph_format.space_before = Pt(before)
    st.paragraph_format.space_after = Pt(after)
    st.paragraph_format.keep_with_next = True
title_ppr = styles["Title"]._element.get_or_add_pPr()
for border in title_ppr.findall(qn("w:pBdr")):
    title_ppr.remove(border)


def para(text, style=None):
    p = doc.add_paragraph(style=style)
    p.add_run(clean(text))
    return p


def figure(path, caption):
    if not path.exists():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Cm(16.0))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(10)
    run = c.add_run(caption)
    run.italic = True
    run.font.size = Pt(9)


def table(lines):
    rows = [[clean(part.strip()) for part in line.strip().strip("|").split("|")] for line in lines]
    rows = [row for row in rows if not all(re.fullmatch(r":?-{2,}:?", cell or "") for cell in row)]
    if not rows:
        return
    cols = len(rows[0])
    t = doc.add_table(rows=0, cols=cols)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    width = 16.0 / cols
    for i, row in enumerate(rows):
        cells = t.add_row().cells
        for j, value in enumerate(row[:cols]):
            cells[j].text = value
            cells[j].width = Cm(width)
            cells[j].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr = cells[j]._tc.get_or_add_tcPr()
            sh = OxmlElement("w:shd")
            sh.set(qn("w:fill"), "DFEAF2" if i == 0 else ("F7F9FB" if i % 2 == 0 else "FFFFFF"))
            tcpr.append(sh)
            mar = OxmlElement("w:tcMar")
            for side in ("top", "left", "bottom", "right"):
                el = OxmlElement("w:" + side)
                el.set(qn("w:w"), "90")
                el.set(qn("w:type"), "dxa")
                mar.append(el)
            tcpr.append(mar)
            borders = OxmlElement("w:tcBorders")
            for side in ("top", "left", "bottom", "right"):
                el = OxmlElement("w:" + side)
                el.set(qn("w:val"), "single")
                el.set(qn("w:sz"), "4")
                el.set(qn("w:color"), "D9D9D9")
                borders.append(el)
            tcpr.append(borders)
            for p in cells[j].paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.05
                for run in p.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(8.5)
                    run.bold = i == 0
    for cell in t.rows[0].cells:
        for p in cell.paragraphs:
            p.paragraph_format.keep_with_next = True
    header = t.rows[0]._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    header.append(repeat)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


doc.add_paragraph("BÁO CÁO ĐỒ ÁN GIỮA KỲ", style="Title")
para("Phân hệ đóng học phí iBanking")
para("Môn học: Kiến trúc hướng dịch vụ  |  Học kỳ 1 năm học 2026–2027")
para("Trường Đại học Tôn Đức Thắng  |  Khoa Công nghệ thông tin")
para("Nhóm: ........................................   Thành viên: ........................................")
para("Ngày cập nhật: 08/11/2026")
doc.add_heading("Tóm tắt", level=1)
para("Hệ thống mô phỏng việc khách hàng iBanking thanh toán toàn bộ học phí cho sinh viên TDTU. Báo cáo trình bày nghiệp vụ, UML, kiến trúc ba service với database riêng, REST API, cơ sở dữ liệu, mã nguồn, transaction, giao diện và kết quả kiểm thử. Stack tích hợp đã chạy bằng Docker với PostgreSQL và hộp thư thử Mailpit. Luồng thanh toán từ đăng nhập đến email xác nhận đã được kiểm tra; các giới hạn của môi trường mô phỏng được nêu riêng ở cuối báo cáo.")
doc.add_heading("Thông tin đánh giá", level=1)
table(["Nội dung | Trạng thái | Bằng chứng", "--- | --- | ---", "Phân tích nghiệp vụ và sơ đồ | Hoàn thành | Sáu sơ đồ draw.io có thể chỉnh sửa", "Service và REST API | Đã tích hợp | Account, Payment, Notification, Frontend", "Giao dịch và OTP | Đã kiểm thử | 6 test đạt; luồng Docker với email thử", "Xử lý đồng thời | Đã kiểm thử | T21 và T22 đạt trên SQLite và PostgreSQL"])

for source in SOURCES:
    lines = source.read_text(encoding="utf-8").splitlines()
    idx = 0
    in_code = False
    while idx < len(lines):
        line = lines[idx].strip()
        if line.startswith("```"):
            in_code = not in_code
            idx += 1
            continue
        if in_code or not line:
            idx += 1
            continue
        if line.startswith("|"):
            block = []
            while idx < len(lines) and lines[idx].strip().startswith("|"):
                block.append(lines[idx])
                idx += 1
            table(block)
            continue
        if line.startswith("#"):
            level = min(len(line) - len(line.lstrip("#")), 3)
            title = clean(line.lstrip("# "))
            doc.add_heading(title, level=level)
            for prefix, (path, caption) in FIGURES.items():
                if title.startswith(prefix):
                    figure(path, caption)
            idx += 1
            continue
        if line.startswith("- ") or re.match(r"^\d+\. ", line):
            if line.startswith("- "):
                para(line[2:], "List Bullet")
            else:
                para(re.sub(r"^\d+\. ", "", line), "List Number")
            idx += 1
            continue
        para(line)
        idx += 1

footer = section.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer.add_run("Báo cáo giữa kỳ  |  Phân hệ đóng học phí iBanking")
doc.save(OUT)
print(OUT)
