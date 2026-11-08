"""Build the editable iBanking diagrams from the implemented service model.

The diagrams use English labels and deliberately separate the conceptual ERD
requested by the assignment from the physical tables in the running services.
"""

from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MASTER = DOCS / "ibanking-so-do-day-du.drawio"

BLUE = "#E2F1F9"
BLUE_STROKE = "#27749B"
GREEN = "#E5F3E8"
GREEN_STROKE = "#4A9061"
AMBER = "#FFF1D6"
AMBER_STROKE = "#B77E27"
RED = "#FCE7E4"
RED_STROKE = "#BC625A"
GREY = "#F3F6F8"
GREY_STROKE = "#8295A3"
PURPLE = "#EEE9F7"
PURPLE_STROKE = "#8266A4"
DARK = "#173B55"

STYLE = {
    "title": f"text;html=1;convertToSvg=1;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=26;fontStyle=1;fontColor={DARK};strokeColor=none;fillColor=none;",
    "subtitle": "text;html=1;convertToSvg=1;align=left;verticalAlign=middle;whiteSpace=wrap;fontFamily=Arial;fontSize=13;fontColor=#617B8D;strokeColor=none;fillColor=none;",
    "label": f"text;html=1;convertToSvg=1;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=15;fontStyle=1;fontColor={DARK};strokeColor=none;fillColor=none;",
    "actor": f"shape=umlActor;html=1;verticalLabelPosition=bottom;verticalAlign=top;fontFamily=Arial;fontSize=14;fontColor={DARK};",
    "boundary": "swimlane;startSize=38;horizontal=1;container=1;collapsible=0;pointerEvents=0;html=1;fontFamily=Arial;fontSize=16;fontStyle=1;fillColor=#F8FBFD;strokeColor=#95B2C4;strokeWidth=2;",
    "usecase": f"ellipse;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontStyle=1;fontColor={DARK};fillColor={BLUE};strokeColor={BLUE_STROKE};strokeWidth=2;",
    "client": f"rounded=1;arcSize=12;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=16;fontStyle=1;fontColor={DARK};fillColor={PURPLE};strokeColor={PURPLE_STROKE};strokeWidth=2;",
    "service": f"rounded=1;arcSize=12;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=16;fontStyle=1;fontColor={DARK};fillColor={BLUE};strokeColor={BLUE_STROKE};strokeWidth=2;",
    "database": f"shape=cylinder3;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontStyle=1;fontColor={DARK};fillColor={GREEN};strokeColor={GREEN_STROKE};strokeWidth=2;",
    "external": f"rounded=1;arcSize=10;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontColor={DARK};fillColor={GREY};strokeColor={GREY_STROKE};strokeWidth=2;dashed=1;",
    "process": f"rounded=1;arcSize=12;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontStyle=1;fontColor={DARK};fillColor={BLUE};strokeColor={BLUE_STROKE};strokeWidth=2;",
    "decision": f"rhombus;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontStyle=1;fontColor={DARK};fillColor={AMBER};strokeColor={AMBER_STROKE};strokeWidth=2;",
    "success": f"rounded=1;arcSize=12;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontStyle=1;fontColor={DARK};fillColor={GREEN};strokeColor={GREEN_STROKE};strokeWidth=2;",
    "error": f"rounded=1;arcSize=12;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontStyle=1;fontColor={DARK};fillColor={RED};strokeColor={RED_STROKE};strokeWidth=2;",
    "table": f"shape=table;startSize=34;container=1;collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=1;html=1;fontFamily=Arial;fontSize=15;fontStyle=1;fontColor={DARK};fillColor={GREEN};strokeColor={GREEN_STROKE};strokeWidth=2;",
    "table_row": "shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;strokeColor=none;collapsible=0;dropTarget=0;html=1;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=12;fontColor=#24485F;spacingLeft=10;portConstraint=eastwest;",
}

EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#55778B;strokeWidth=2;endArrow=block;endFill=1;fontFamily=Arial;fontSize=12;fontColor=#47657A;labelBackgroundColor=#FFFFFF;"
ASSOC = EDGE + "endArrow=none;"
DASH = EDGE + "dashed=1;endArrow=open;endFill=0;"
ER = EDGE + "startArrow=ERmandOne;endArrow=ERmany;startFill=0;endFill=0;"
ER_ONE = EDGE + "startArrow=ERmandOne;endArrow=ERone;startFill=0;endFill=0;"
LOGICAL = ER + "dashed=1;"

mxfile = ET.Element("mxfile", {"host": "drawio", "version": "26.0.0", "type": "device"})
pages = []


def page(number, name, stem, width, height, subtitle):
    diagram = ET.SubElement(mxfile, "diagram", {"id": stem, "name": f"{number:02d} {name}"})
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": str(width), "dy": str(height), "grid": "1", "gridSize": "10",
            "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
            "fold": "1", "page": "1", "pageScale": "1", "pageWidth": str(width),
            "pageHeight": str(height), "background": "#FFFFFF", "math": "0", "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    box(root, f"{stem}-title", name.upper(), 42, 24, width - 84, 48, "title")
    box(root, f"{stem}-subtitle", subtitle, 44, 76, width - 88, 36, "subtitle")
    pages.append((diagram, stem))
    return root


def box(root, cell_id, value, x, y, width, height, kind="process", parent="1", style=None, source=None):
    attrs = {"id": cell_id, "value": value, "style": style or STYLE[kind], "vertex": "1", "parent": parent}
    if source:
        attrs["data-source"] = source
    cell = ET.SubElement(root, "mxCell", attrs)
    ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})
    return cell


def link(root, edge_id, source, target, label="", style=EDGE, points=None):
    cell = ET.SubElement(root, "mxCell", {"id": edge_id, "value": label, "style": style, "edge": "1", "parent": "1", "source": source, "target": target})
    geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    if points:
        array = ET.SubElement(geometry, "Array", {"as": "points"})
        for x, y in points:
            ET.SubElement(array, "mxPoint", {"x": str(x), "y": str(y)})


def entity(root, cell_id, title, fields, x, y, width=285, source=None):
    row_height = 25
    height = 34 + len(fields) * row_height + 5
    box(root, cell_id, title, x, y, width, height, "table", source=source)
    for index, field in enumerate(fields):
        style = STYLE["table_row"] + ("fontStyle=1;" if field.startswith("PK ") else "")
        box(root, f"{cell_id}-row-{index}", field, 0, 34 + index * row_height, width, row_height, "table_row", parent=cell_id, style=style)
    return height


# 01: UML Use Case. Databases and backend services are inside the boundary, not actors.
r = page(1, "Use Case Diagram", "01-use-case", 1450, 835,
         "Customer goals and the external email provider; payment is always for the full tuition amount.")
box(r, "uc-user", "Customer", 82, 323, 86, 120, "actor")
box(r, "uc-email", "Email provider", 1280, 323, 90, 120, "actor")
box(r, "uc-system", "iBanking Tuition Payment Subsystem", 255, 142, 925, 595, "boundary")
for cell_id, title, x, y in [
    ("uc01", "UC01  Log in", 62, 73),
    ("uc02", "UC02  View profile\nand balance", 536, 73),
    ("uc03", "UC03  Look up tuition\nby student ID", 62, 232),
    ("uc04", "UC04  Create full\npayment", 536, 232),
    ("uc05", "UC05  Confirm payment\nwith email OTP", 62, 391),
    ("uc06", "UC06  Commit payment\nand send receipt", 536, 391),
]:
    box(r, cell_id, title, x, y, 310, 82, "usecase", parent="uc-system")
for i, target in enumerate(("uc01", "uc02", "uc03", "uc04", "uc05"), 1):
    link(r, f"uc-user-{i}", "uc-user", target, style=ASSOC)
link(r, "uc-email-otp", "uc-email", "uc04", style=ASSOC)
link(r, "uc-email-receipt", "uc-email", "uc06", style=ASSOC)
link(r, "uc-include", "uc04", "uc03", "<<include>>", DASH)
link(r, "uc-extend", "uc06", "uc05", "<<extend>>", DASH)
box(r, "uc-note", "UC06 runs after a valid OTP. Database is an internal data store, not a UML actor.", 260, 760, 1030, 32, "subtitle")


# 02: Declared and implemented Docker Compose architecture.
r = page(2, "Microservices Architecture", "02-microservices-architecture", 1600, 955,
         "Three services own separate logical PostgreSQL databases; SMTP is outside the service boundary.")
box(r, "ar-customer", "Customer\n(browser)", 55, 385, 180, 82, "client")
box(r, "ar-frontend", "Frontend\nReact + Vite :5173", 310, 375, 270, 100, "client", source="src/frontend; src/compose.yaml")
box(r, "ar-account", "Account Service\nlogin · profile · JWT\nFastAPI :8081", 685, 155, 300, 112, "service", source="src/services/account/app.py")
box(r, "ar-payment", "Payment Service\nwallet · tuition · OTP · transaction\nFastAPI :8082", 685, 370, 300, 130, "service", source="src/services/payment/app.py")
box(r, "ar-notification", "Notification Service\nemail · messageId idempotency\nFastAPI :8083", 685, 625, 300, 120, "service", source="src/services/notification/app.py")
box(r, "ar-postgres", "PostgreSQL 16 instance", 1105, 130, 380, 665, "boundary")
box(r, "ar-account-db", "Account DB\nusers", 55, 64, 270, 100, "database", parent="ar-postgres")
box(r, "ar-payment-db", "Payment DB\nwallets · students · tuitions\npayments · otps · email_jobs", 55, 270, 270, 126, "database", parent="ar-postgres")
box(r, "ar-notification-db", "Notification DB\nemail_messages", 55, 500, 270, 100, "database", parent="ar-postgres")
box(r, "ar-smtp", "SMTP server\nMailpit for local demo", 1160, 835, 270, 76, "external", source="src/compose.yaml")
for edge_id, source, target, label in [
    ("ar-1", "ar-customer", "ar-frontend", "Browser UI / HTTP demo"),
    ("ar-2", "ar-frontend", "ar-account", "REST login / profile"),
    ("ar-3", "ar-frontend", "ar-payment", "REST + Bearer JWT"),
    ("ar-4", "ar-payment", "ar-notification", "Internal REST + X-Internal-Key"),
    ("ar-5", "ar-account", "ar-account-db", "SQL"),
    ("ar-6", "ar-payment", "ar-payment-db", "SQL transaction"),
    ("ar-7", "ar-notification", "ar-notification-db", "SQL"),
    ("ar-8", "ar-notification", "ar-smtp", "SMTP"),
]:
    link(r, edge_id, source, target, label)
box(r, "ar-footer", "Blue: services  |  Purple: client  |  Green: owned database  |  Gray dashed: external service", 42, 870, 930, 35, "subtitle")


# 03: The five assignment-level entities, independent of physical service ownership.
r = page(3, "Conceptual ERD", "03-conceptual-erd", 1460, 915,
         "Five core business entities from the assignment; Wallet and email tables appear in the physical ERD.")
entity(r, "co-users", "Users", ["PK user_id", "UQ username", "full_name · phone · email", "available_balance (conceptual)"], 75, 195, 290)
entity(r, "co-students", "Students", ["PK student_id (MSSV)", "student_name"], 590, 195, 290)
entity(r, "co-tuitions", "Tuitions", ["PK tuition_id", "FK student_id", "amount · status", "paid_at"], 1050, 195, 290)
entity(r, "co-transactions", "Transactions", ["PK transaction_id", "FK user_id · FK tuition_id", "amount · status", "created_at · paid_at"], 420, 545, 320)
entity(r, "co-otps", "OTPs", ["PK otp_id", "FK transaction_id (unique)", "code_hash · expires_at", "used_at"], 975, 545, 300)
link(r, "co-rel-1", "co-users", "co-transactions", "1 to many", ER)
link(r, "co-rel-2", "co-students", "co-tuitions", "1 to many", ER)
link(r, "co-rel-3", "co-tuitions", "co-transactions", "1 to many", ER)
link(r, "co-rel-4", "co-transactions", "co-otps", "1 to 0..1", ER_ONE)
box(r, "co-note", "Conceptual Transaction maps to physical payments; available_balance maps to wallets.balance.", 80, 805, 1260, 35, "subtitle")


# 04: Physical tables from current SQL migrations and SQLAlchemy models.
r = page(4, "Physical ERD", "04-physical-erd", 1810, 1160,
         "Eight implemented tables across Account, Payment and Notification databases. Dashed links cross databases.")
box(r, "ph-account-label", "ACCOUNT DB", 58, 142, 300, 36, "label")
box(r, "ph-payment-label", "PAYMENT DB", 495, 142, 850, 36, "label")
box(r, "ph-notification-label", "NOTIFICATION DB", 1475, 142, 300, 36, "label")
entity(r, "ph-users", "users", ["PK id", "UQ username", "password_hash", "full_name · phone · email"], 55, 198, 305, source="src/services/account/migrations/001_users.sql")
entity(r, "ph-wallets", "wallets", ["PK user_id", "balance >= 0", "currency"], 490, 198, 300, source="src/services/payment/app.py:37")
entity(r, "ph-students", "students", ["PK student_id", "full_name"], 925, 198, 300, source="src/services/payment/app.py:47")
entity(r, "ph-tuitions", "tuitions", ["PK tuition_id", "FK student_id", "amount > 0", "status · paid_at"], 925, 495, 300, source="src/services/payment/app.py:53")
entity(r, "ph-payments", "payments", ["PK payment_id", "user_id (logical ref)", "FK tuition_id", "UQ (user_id, request_id)", "amount · status", "created_at · otp_expires_at", "paid_at · failure_code"], 490, 480, 325, source="src/services/payment/app.py:64")
entity(r, "ph-otps", "otps", ["PK otp_id", "FK payment_id (unique)", "code_hash", "issued_at · expires_at", "used_at"], 490, 825, 305, source="src/services/payment/app.py:81")
entity(r, "ph-jobs", "email_jobs", ["PK job_id", "FK payment_id (unique)", "email_to · status", "attempts"], 925, 825, 300, source="src/services/payment/app.py:90")
entity(r, "ph-messages", "email_messages", ["PK message_id", "payload_hash", "status · updated_at"], 1470, 198, 305, source="src/services/notification/migrations/001_messages.sql")
link(r, "ph-rel-users-wallets", "ph-users", "ph-wallets", "1 : 1 logical", LOGICAL)
link(r, "ph-rel-users-payments", "ph-users", "ph-payments", "1 : many logical", LOGICAL, [(398, 420), (430, 600)])
link(r, "ph-rel-students-tuitions", "ph-students", "ph-tuitions", "1 : many", ER)
link(r, "ph-rel-tuitions-payments", "ph-tuitions", "ph-payments", "1 : many", ER)
link(r, "ph-rel-payments-otps", "ph-payments", "ph-otps", "1 : 0..1", ER_ONE)
link(r, "ph-rel-payments-jobs", "ph-payments", "ph-jobs", "1 : 0..1", ER_ONE)
link(r, "ph-rel-jobs-messages", "ph-jobs", "ph-messages", "messageId via API", DASH, [(1400, 975), (1400, 400)])
box(r, "ph-note", "Physical constraints: wallet_nonnegative, tuition_positive, unique payment request, one OTP and one receipt job per payment. No foreign keys across databases.", 55, 1070, 1690, 48, "subtitle")


# 05: Two-phase payment flow, including the transactional boundary and receipt job.
r = page(5, "Payment and OTP Flow", "05-payment-otp-flow", 1580, 940,
         "Create does not debit the wallet. Confirm performs the financial update in one database transaction.")
for cell_id, title, x, y, kind in [
    ("fl-lookup", "Log in and\nlook up tuition", 55, 200, "process"),
    ("fl-check", "Check UNPAID\nand balance", 345, 200, "decision"),
    ("fl-create", "Save PENDING_OTP\nand hashed OTP", 655, 200, "process"),
    ("fl-email", "Send OTP email\nTTL 5 minutes", 965, 200, "process"),
    ("fl-enter", "Customer enters OTP", 1265, 200, "process"),
    ("fl-lock", "Lock payment, OTP,\nwallet and tuition", 1265, 505, "process"),
    ("fl-recheck", "Recheck OTP, status\nand balance", 950, 505, "decision"),
    ("fl-commit", "Atomic commit\ndebit · PAID · SUCCESS\nuse OTP · create receipt job", 620, 495, "success"),
    ("fl-job", "Send receipt email\nretry if delivery fails", 315, 505, "process"),
    ("fl-done", "Payment complete", 55, 505, "success"),
]:
    box(r, cell_id, title, x, y, 245, 110, kind)
for edge_id, source, target, label in [
    ("fl-1", "fl-lookup", "fl-check", ""),
    ("fl-2", "fl-check", "fl-create", "eligible"),
    ("fl-3", "fl-create", "fl-email", ""),
    ("fl-4", "fl-email", "fl-enter", ""),
    ("fl-5", "fl-enter", "fl-lock", "confirm"),
    ("fl-6", "fl-lock", "fl-recheck", ""),
    ("fl-7", "fl-recheck", "fl-commit", "valid"),
    ("fl-8", "fl-commit", "fl-job", "after commit"),
    ("fl-9", "fl-job", "fl-done", ""),
]:
    link(r, edge_id, source, target, label)
box(r, "fl-error", "Invalid / expired OTP, insufficient balance or already-paid tuition: no debit. Technical failure before commit: rollback.", 360, 755, 900, 80, "error")
link(r, "fl-error-check", "fl-recheck", "fl-error", "reject", DASH)
box(r, "fl-foot", "The receipt job is committed with the payment. Notification uses messageId to avoid duplicate emails during retry.", 65, 860, 1400, 35, "subtitle")


# 06: The two required concurrency scenarios, with observed response outcomes.
r = page(6, "Concurrency and Consistency", "06-concurrency", 1560, 1030,
         "PostgreSQL SELECT FOR UPDATE serializes conflicting confirmations; both scenarios are tested on the live stack.")
box(r, "cc-t21-title", "T21  |  SAME WALLET, TWO TUITION CHARGES", 65, 145, 1430, 38, "label")
box(r, "cc-a", "Payment A\n7M VND", 85, 230, 220, 88, "process")
box(r, "cc-b", "Payment B\n7M VND", 85, 365, 220, 88, "process")
box(r, "cc-wallet", "Lock wallet row\nstarting balance 10M", 520, 285, 300, 110, "decision")
box(r, "cc-a-win", "One SUCCESS\nfinal balance 3M", 1050, 230, 330, 88, "success")
box(r, "cc-b-lose", "Other: 422\nINSUFFICIENT_BALANCE", 1050, 365, 330, 88, "error")
for edge_id, source, target, label in [
    ("cc-1", "cc-a", "cc-wallet", "confirm"), ("cc-2", "cc-b", "cc-wallet", "confirm"),
    ("cc-3", "cc-wallet", "cc-a-win", "first commit"), ("cc-4", "cc-wallet", "cc-b-lose", "recheck 3M < 7M"),
]:
    link(r, edge_id, source, target, label)
box(r, "cc-t22-title", "T22  |  TWO WALLETS, SAME TUITION CHARGE", 65, 525, 1430, 38, "label")
box(r, "cc-u1", "Wallet 1 pays\nsame tuition", 85, 610, 220, 88, "process")
box(r, "cc-u2", "Wallet 2 pays\nsame tuition", 85, 745, 220, 88, "process")
box(r, "cc-tuition", "Lock tuition row\ncheck UNPAID", 520, 665, 300, 110, "decision")
box(r, "cc-paid", "One SUCCESS\ntuition becomes PAID", 1050, 610, 330, 88, "success")
box(r, "cc-reject", "Other: 409 TUITION_ALREADY_PAID\nsecond wallet unchanged", 1050, 745, 330, 88, "error")
for edge_id, source, target, label in [
    ("cc-5", "cc-u1", "cc-tuition", "confirm"), ("cc-6", "cc-u2", "cc-tuition", "confirm"),
    ("cc-7", "cc-tuition", "cc-paid", "first commit"), ("cc-8", "cc-tuition", "cc-reject", "recheck PAID"),
]:
    link(r, edge_id, source, target, label)
box(r, "cc-foot", "Source: src/services/payment/app.py and src/tests/integration_postgres.py. SQLite tests use BEGIN IMMEDIATE instead of row locks.", 65, 915, 1420, 45, "subtitle")


def save_xml(destination, file_root):
    ET.indent(file_root, space="  ")
    payload = ET.tostring(file_root, encoding="utf-8", xml_declaration=True)
    destination.write_bytes(payload.replace(b"&#10;", b"&#xa;"))


save_xml(MASTER, mxfile)
for diagram, stem in pages:
    single = ET.Element("mxfile", {"host": "drawio", "version": "26.0.0", "type": "device"})
    single.append(ET.fromstring(ET.tostring(diagram, encoding="utf-8")))
    save_xml(DOCS / f"{stem}.drawio", single)

# Keep the existing filenames used by the report and project links in sync.
aliases = {
    "01-phan-tich-nghiep-vu-use-case.drawio": "01-use-case.drawio",
    "01-tuition-payment-use-case.drawio": "01-use-case.drawio",
    "01-use-case-nghiep-vu.drawio": "01-use-case.drawio",
    "01-phan-tich-nghiep-vu-erd.drawio": "03-conceptual-erd.drawio",
    "02-tuition-payment-microservices-architecture.drawio": "02-microservices-architecture.drawio",
    "02-microservices-architecture-clear.drawio": "02-microservices-architecture.drawio",
    "02-microservices-architecture-visual.drawio": "02-microservices-architecture.drawio",
    "03-tuition-payment-erd.drawio": "04-physical-erd.drawio",
    "03-erd.drawio": "04-physical-erd.drawio",
    "04-payment-otp-flow.drawio": "05-payment-otp-flow.drawio",
    "05-concurrency.drawio": "06-concurrency.drawio",
}
for alias, canonical in aliases.items():
    (DOCS / alias).write_bytes((DOCS / canonical).read_bytes())

print(MASTER)
for _, stem in pages:
    print(DOCS / f"{stem}.drawio")
