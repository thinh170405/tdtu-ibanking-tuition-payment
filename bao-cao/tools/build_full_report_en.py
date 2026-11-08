"""Build the English midterm report from its reviewed Markdown source."""

import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "ibanking-midterm-report-en.md"
OUTPUT = ROOT / "ibanking-midterm-report-en.docx"
FIGURES = {
    1: ROOT / "docs/previews/01-use-case-final.png",
    2: ROOT / "docs/previews/03-conceptual-erd-final.png",
    3: ROOT / "docs/previews/02-microservices-architecture-final.png",
    4: ROOT / "docs/previews/04-physical-erd-final.png",
    5: ROOT / "docs/previews/05-payment-otp-flow-final.png",
    6: ROOT / "docs/previews/06-concurrency-final.png",
}


def set_cell_border(cell):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        node = OxmlElement(f"w:{edge}")
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "4")
        node.set(qn("w:color"), "D9D9D9")
        borders.append(node)
    tc_pr.append(borders)
    margins = OxmlElement("w:tcMar")
    for edge in ("top", "left", "bottom", "right"):
        node = OxmlElement(f"w:{edge}")
        node.set(qn("w:w"), "95")
        node.set(qn("w:type"), "dxa")
        margins.append(node)
    tc_pr.append(margins)


def add_rich(paragraph, value):
    value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", value):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9)
        else:
            paragraph.add_run(part)


def add_paragraph(doc, value, style=None):
    paragraph = doc.add_paragraph(style=style)
    add_rich(paragraph, value)
    return paragraph


def add_table(doc, lines):
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    rows = [row for row in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in row)]
    cols = len(rows[0])
    table = doc.add_table(rows=0, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    full_width = 6.9
    fractions = {3: [0.22, 0.35, 0.43], 4: [0.15, 0.12, 0.48, 0.25]}.get(cols, [1 / cols] * cols)
    for col_index, fraction in enumerate(fractions):
        table.columns[col_index].width = Inches(full_width * fraction)
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for col_index, value in enumerate(row):
            cell = cells[col_index]
            cell.width = Inches(full_width * fractions[col_index])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_border(cell)
            shading = OxmlElement("w:shd")
            shading.set(qn("w:fill"), "DCE8F0" if row_index == 0 else ("F4F7FA" if row_index % 2 == 0 else "FFFFFF"))
            cell._tc.get_or_add_tcPr().append(shading)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.08
            add_rich(paragraph, value)
            for run in paragraph.runs:
                run.font.size = Pt(8.8)
                if row_index == 0:
                    run.bold = True
    first = table.rows[0]._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    first.append(repeat)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_figure(doc, number, caption):
    path = FIGURES[number]
    if not path.exists():
        raise FileNotFoundError(path)
    image = doc.add_paragraph()
    image.alignment = WD_ALIGN_PARAGRAPH.CENTER
    image.paragraph_format.space_before = Pt(7)
    image.paragraph_format.space_after = Pt(4)
    image.paragraph_format.keep_with_next = True
    image.add_run().add_picture(str(path), width=Inches(6.7))
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(12)
    run = paragraph.add_run(caption)
    run.italic = True
    run.font.size = Pt(9)


def add_field(paragraph, name):
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), name)
    paragraph._p.append(field)


def main():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.78)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12
    for style_name, size, before, after in [
        ("Title", 21, 0, 14),
        ("Heading 1", 15, 17, 7),
        ("Heading 2", 12, 12, 5),
        ("Heading 3", 10.5, 9, 4),
    ]:
        style = styles[style_name]
        style.font.name = "Aptos Display" if style_name == "Title" else "Aptos"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
    title_ppr = styles["Title"]._element.get_or_add_pPr()
    for border in title_ppr.findall(qn("w:pBdr")):
        title_ppr.remove(border)

    # Cover with fillable group details. No member names are invented.
    doc.add_paragraph("TON DUC THANG UNIVERSITY", style="Normal").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Faculty of Information Technology", style="Normal").alignment = WD_ALIGN_PARAGRAPH.CENTER
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(65)
    title = doc.add_paragraph("iBanking Tuition Payment", style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle = doc.add_paragraph("Midterm Project Report", style="Heading 1")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta = doc.add_paragraph("Service Oriented Architecture  |  Academic Year 2026 to 2027")
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    doc.add_paragraph("Group: ______________________________")
    doc.add_paragraph("Members: ____________________________")
    doc.add_paragraph("Instructor: __________________________")
    doc.add_paragraph("November 2026").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("# "):
            index += 1  # Already used on the cover.
            continue
        if line.startswith("|"):
            block = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                block.append(lines[index].strip())
                index += 1
            add_table(doc, block)
            continue
        figure = re.match(r"Figure ([1-6])\. (.+)", line)
        if figure:
            add_figure(doc, int(figure.group(1)), line)
            index += 1
            continue
        if line.startswith("## "):
            doc.add_heading(line[3:], level=1)
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=2)
        elif line.startswith("- "):
            add_paragraph(doc, line[2:], "List Bullet")
        else:
            add_paragraph(doc, line)
        index += 1

    header = section.header.paragraphs[0]
    header.text = "iBanking Tuition Payment  |  Midterm Project Report"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in header.runs:
        run.font.name = "Aptos"
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(90, 90, 90)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Page ")
    add_field(footer, "PAGE")

    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
