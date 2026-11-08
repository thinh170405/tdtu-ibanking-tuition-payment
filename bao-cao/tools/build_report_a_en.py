from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

root = Path(__file__).resolve().parents[1]
source = root / "docs" / "report-A.md"
output = root / "ibanking-part-A-report-en.docx"
doc = Document()
section = doc.sections[0]
section.top_margin = Inches(0.8)
section.bottom_margin = Inches(0.8)
section.left_margin = Inches(0.9)
section.right_margin = Inches(0.9)
normal = doc.styles["Normal"]
normal.font.name = "Arial"
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(6)
for name, size in (("Title", 18), ("Heading 1", 13)):
    style = doc.styles[name]
    style.font.name = "Arial"
    style.font.size = Pt(size)
    style.font.bold = True
    style.paragraph_format.space_before = Pt(11)
    style.paragraph_format.space_after = Pt(6)

lines = source.read_text(encoding="utf-8").splitlines()
i = 0
while i < len(lines):
    line = lines[i].strip()
    if not line:
        i += 1
        continue
    if line.startswith("# "):
        doc.add_paragraph(line[2:], "Title")
    elif line.startswith("## "):
        doc.add_paragraph(line[3:], "Heading 1")
    elif line.startswith("|"):
        block = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            block.append(lines[i].strip())
            i += 1
        rows = [[cell.strip().replace("`", "") for cell in row.strip("|").split("|")] for row in block]
        rows = [row for row in rows if not all(set(cell) <= {"-", ":"} for cell in row)]
        table = doc.add_table(rows=0, cols=len(rows[0]))
        table.style = "Table Grid"
        for row in rows:
            cells = table.add_row().cells
            for j, value in enumerate(row):
                cells[j].text = value
        for cell in table.rows[0].cells:
            for run in cell.paragraphs[0].runs:
                run.bold = True
        continue
    elif line.startswith("- "):
        doc.add_paragraph(line[2:].replace("`", ""), "List Bullet")
    else:
        doc.add_paragraph(line.replace("`", "").replace("**", ""))
    i += 1

footer = section.footer.paragraphs[0]
footer.text = "iBanking Tuition Payment — Part A"
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.save(output)
print(output)
