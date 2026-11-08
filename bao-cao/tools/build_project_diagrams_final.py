"""Build the editable iBanking diagrams from the implemented service model.

The diagrams use English labels and deliberately separate the conceptual ERD
requested by the assignment from the physical tables in the running services.
"""

from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MASTER = DOCS / "ibanking-diagrams-final.drawio"

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
    "table": f"shape=table;startSize=36;container=1;collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=1;html=1;fontFamily=Arial;fontSize=15;fontStyle=1;fontColor={DARK};fillColor={GREEN};strokeColor={GREEN_STROKE};strokeWidth=2;",
    "table_row": "shape=tableRow;horizontal=1;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;strokeColor=none;collapsible=0;dropTarget=0;html=1;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=13;fontColor=#24485F;spacingLeft=12;portConstraint=eastwest;",
}

EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#55778B;strokeWidth=2;endArrow=block;endFill=1;fontFamily=Arial;fontSize=12;fontColor=#47657A;labelBackgroundColor=#FFFFFF;"
ASSOC = "edgeStyle=none;html=1;strokeColor=#55778B;strokeWidth=2;endArrow=none;"
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


def anchors(style, exit_x, exit_y, entry_x, entry_y):
    return (style + f"exitX={exit_x};exitY={exit_y};exitDx=0;exitDy=0;"
            f"entryX={entry_x};entryY={entry_y};entryDx=0;entryDy=0;")


def entity(root, cell_id, title, fields, x, y, width=285, source=None, parent="1"):
    row_height = 27
    height = 36 + len(fields) * row_height + 5
    box(root, cell_id, title, x, y, width, height, "table", parent=parent, source=source)
    for index, field in enumerate(fields):
        style = STYLE["table_row"] + ("fontStyle=1;" if field.startswith("PK ") else "")
        box(root, f"{cell_id}-row-{index}", field, 0, 36 + index * row_height, width, row_height, "table_row", parent=cell_id, style=style)
    return height


# 01: UML Use Case. Databases and backend services are inside the boundary, not actors.
r = page(1, "Use Case Diagram", "01-use-case", 1500, 1070,
         "Customer goals, email delivery and the full-amount tuition payment rule.")
box(r, "uc-user", "Customer", 80, 480, 100, 130, "actor")
box(r, "uc-email", "Email provider", 1300, 450, 100, 130, "actor")
box(r, "uc-system", "iBanking Tuition Payment Subsystem", 255, 150, 920, 795, "boundary")
for cell_id, title, x, y in [
    ("uc01", "UC01  Log in", 120, 75),
    ("uc02", "UC02  View profile\nand balance", 120, 205),
    ("uc03", "UC03  Look up tuition\nby student ID", 120, 335),
    ("uc04", "UC04  Create full\npayment", 120, 465),
    ("uc05", "UC05  Confirm payment\nwith email OTP", 120, 595),
    ("uc06", "UC06  Commit payment\nand send receipt", 585, 595),
]:
    box(r, cell_id, title, x, y, 300, 78, "usecase", parent="uc-system")
for i, target in enumerate(("uc01", "uc02", "uc03", "uc04", "uc05"), 1):
    link(r, f"uc-user-{i}", "uc-user", target,
         style=anchors(ASSOC, 1, 0.45, 0, 0.5))
link(r, "uc-email-otp", "uc-email", "uc04", style=anchors(ASSOC, 0, 0.45, 1, 0.5))
link(r, "uc-email-receipt", "uc-email", "uc06", style=anchors(ASSOC, 0, 0.55, 1, 0.5))
link(r, "uc-include", "uc04", "uc03", "«include»", anchors(DASH, 0.5, 0, 0.5, 1))
link(r, "uc-extend", "uc06", "uc05", "«extend»", anchors(DASH, 0, 0.5, 1, 0.5))
box(r, "uc-note", "UC06 executes only after UC05 validates the OTP. The database is an internal data store, not an actor.", 280, 985, 1120, 35, "subtitle")


# 02: Declared and implemented Docker Compose architecture.
r = page(2, "Microservices Architecture", "02-microservices-architecture", 1740, 1080,
         "One PostgreSQL instance hosts three separately owned databases; Mailpit receives SMTP in the local demo.")
box(r, "ar-customer", "Customer\n(browser)", 55, 465, 185, 85, "client")
box(r, "ar-frontend", "Frontend\nReact + Vite :5173", 325, 455, 285, 110, "client", source="src/frontend; src/compose.yaml")
box(r, "ar-account", "Account Service\nlogin · profile · JWT\nFastAPI :8081", 750, 205, 320, 120, "service", source="src/services/account/app.py")
box(r, "ar-payment", "Payment Service\nwallet · tuition · OTP · transaction\nFastAPI :8082", 750, 455, 320, 130, "service", source="src/services/payment/app.py")
box(r, "ar-notification", "Notification Service\nemail · messageId idempotency\nFastAPI :8083", 750, 705, 320, 120, "service", source="src/services/notification/app.py")
box(r, "ar-postgres", "PostgreSQL 16 instance", 1220, 150, 450, 720, "boundary")
box(r, "ar-account-db", "Account DB\nusers", 60, 70, 330, 100, "database", parent="ar-postgres")
box(r, "ar-payment-db", "Payment DB\nwallets · students · tuitions\npayments · otps · email_jobs", 60, 315, 330, 120, "database", parent="ar-postgres")
box(r, "ar-notification-db", "Notification DB\nemail_messages", 60, 560, 330, 100, "database", parent="ar-postgres")
box(r, "ar-smtp", "SMTP server\nMailpit for local demo", 790, 910, 280, 85, "external", source="src/compose.yaml")
link(r, "ar-1", "ar-customer", "ar-frontend", "HTTP demo",
     anchors(EDGE, 1, 0.5, 0, 0.5))
link(r, "ar-2", "ar-frontend", "ar-account", "REST login / profile",
     anchors(EDGE, 1, 0.15, 0, 0.5), [(680, 265)])
link(r, "ar-3", "ar-frontend", "ar-payment", "REST + Bearer JWT",
     anchors(EDGE, 1, 0.6, 0, 0.5))
link(r, "ar-4", "ar-payment", "ar-notification", "Internal REST + X-Internal-Key",
     anchors(EDGE, 0.5, 1, 0.5, 0))
link(r, "ar-5", "ar-account", "ar-account-db", "SQL",
     anchors(EDGE, 1, 0.5, 0, 0.5))
link(r, "ar-6", "ar-payment", "ar-payment-db", "SQL transaction",
     anchors(EDGE, 1, 0.5, 0, 0.5))
link(r, "ar-7", "ar-notification", "ar-notification-db", "SQL",
     anchors(EDGE, 1, 0.5, 0, 0.5))
link(r, "ar-8", "ar-notification", "ar-smtp", "SMTP",
     anchors(EDGE, 0.5, 1, 0.5, 0))
box(r, "ar-footer", "Payment validates the JWT locally. Blue: service  |  Purple: client  |  Green: owned database  |  Dashed gray: external SMTP", 55, 1015, 1550, 35, "subtitle")


# 03: The five assignment-level entities, independent of physical service ownership.
r = page(3, "Conceptual ERD", "03-conceptual-erd", 1550, 930,
         "Five core business entities from the assignment; Wallet and email tables appear in the physical ERD.")
entity(r, "co-users", "Users", ["PK user_id", "UQ username", "full_name · phone · email", "available_balance (conceptual)"], 70, 230, 300)
entity(r, "co-students", "Students", ["PK student_id (MSSV)", "student_name"], 620, 230, 300)
entity(r, "co-tuitions", "Tuitions", ["PK tuition_id", "FK student_id", "amount · status", "paid_at"], 1160, 230, 300)
entity(r, "co-transactions", "Transactions", ["PK transaction_id", "FK user_id · FK tuition_id", "amount · status", "created_at · paid_at"], 360, 600, 340)
entity(r, "co-otps", "OTPs", ["PK otp_id", "FK transaction_id (unique)", "code_hash · expires_at", "used_at"], 930, 600, 310)
link(r, "co-rel-1", "co-users", "co-transactions", "1 : N",
     anchors(ER, 0.5, 1, 0.3, 0), [(220, 500), (460, 500)])
link(r, "co-rel-2", "co-students", "co-tuitions", "1 : N",
     anchors(ER, 1, 0.5, 0, 0.5))
link(r, "co-rel-3", "co-tuitions", "co-transactions", "1 : N",
     anchors(ER, 0.5, 1, 1, 0.5), [(1310, 510), (770, 510), (770, 670)])
link(r, "co-rel-4", "co-transactions", "co-otps", "1 : 0..1",
     anchors(ER_ONE, 1, 0.5, 0, 0.5))
box(r, "co-note", "Conceptual Transactions map to physical payments; available_balance maps to wallets.balance.", 75, 850, 1340, 35, "subtitle")


# 04: Physical tables from current SQL migrations and SQLAlchemy models.
r = page(4, "Physical ERD", "04-physical-erd", 1900, 1300,
         "Eight implemented tables. Solid crow's-foot links are database foreign keys; dashed links are logical references.")
group_style = "swimlane;startSize=42;horizontal=1;container=1;collapsible=0;pointerEvents=0;html=1;fontFamily=Arial;fontSize=17;fontStyle=1;fontColor=#173B55;strokeWidth=2;"
box(r, "ph-account-db", "ACCOUNT DB", 45, 160, 340, 1080, style=group_style + "fillColor=#F8FBFD;strokeColor=#B9CEDA;")
box(r, "ph-payment-db", "PAYMENT DB", 420, 160, 1010, 1080, style=group_style + "fillColor=#F8FCF9;strokeColor=#A8CFB4;")
box(r, "ph-notification-db", "NOTIFICATION DB", 1460, 160, 390, 1080, style=group_style + "fillColor=#FAF9FD;strokeColor=#C9C0DA;")
entity(r, "ph-users", "users", ["PK id", "UQ username", "password_hash", "full_name", "phone", "email"], 20, 75, 300,
       source="src/services/account/migrations/001_users.sql", parent="ph-account-db")
entity(r, "ph-wallets", "wallets", ["PK user_id (logical user ref)", "balance CHECK >= 0", "currency"], 30, 75, 350,
       source="src/services/payment/app.py:37", parent="ph-payment-db")
entity(r, "ph-students", "students", ["PK student_id (MSSV)", "full_name"], 520, 75, 310,
       source="src/services/payment/app.py:47", parent="ph-payment-db")
entity(r, "ph-payments", "payments", ["PK payment_id", "user_id (logical user ref)", "FK tuition_id", "UQ (user_id, request_id)", "amount", "status", "created_at", "otp_expires_at", "paid_at", "failure_code"], 30, 360, 350,
       source="src/services/payment/app.py:64", parent="ph-payment-db")
entity(r, "ph-tuitions", "tuitions", ["PK tuition_id", "FK student_id", "amount CHECK > 0", "status", "paid_at"], 520, 360, 310,
       source="src/services/payment/app.py:53", parent="ph-payment-db")
entity(r, "ph-otps", "otps", ["PK otp_id", "FK payment_id UQ", "code_hash", "issued_at", "expires_at", "used_at"], 30, 755, 350,
       source="src/services/payment/app.py:81", parent="ph-payment-db")
entity(r, "ph-jobs", "email_jobs", ["PK job_id", "FK payment_id UQ", "email_to", "status", "attempts"], 520, 755, 310,
       source="src/services/payment/app.py:90", parent="ph-payment-db")
entity(r, "ph-messages", "email_messages", ["PK message_id", "payload_hash", "status", "updated_at"], 35, 75, 320,
       source="src/services/notification/migrations/001_messages.sql", parent="ph-notification-db")
link(r, "ph-rel-users-wallets", "ph-users", "ph-wallets", "1 : 1 logical",
     anchors(LOGICAL, 1, 0.35, 0, 0.5))
link(r, "ph-rel-users-payments", "ph-users", "ph-payments", "1 : N logical",
     anchors(LOGICAL, 0.5, 1, 0, 0.5), [(215, 620), (405, 620)])
link(r, "ph-rel-students-tuitions", "ph-students", "ph-tuitions", "1 : N",
     anchors(ER, 0.5, 1, 0.5, 0))
link(r, "ph-rel-tuitions-payments", "ph-tuitions", "ph-payments", "1 : N",
     anchors(ER, 0, 0.5, 1, 0.5))
link(r, "ph-rel-payments-otps", "ph-payments", "ph-otps", "1 : 0..1",
     anchors(ER_ONE, 0.5, 1, 0.5, 0))
link(r, "ph-rel-payments-jobs", "ph-payments", "ph-jobs", "1 : 0..1",
     anchors(ER_ONE, 1, 0.7, 0, 0.5), [(870, 735), (870, 1000)])
link(r, "ph-rel-jobs-messages", "ph-jobs", "ph-messages", "messageId via API",
     anchors(DASH, 1, 0.5, 0, 0.5), [(1445, 1000), (1445, 330)])
box(r, "ph-note", "Constraints: wallet_nonnegative, tuition_positive, unique payment request, one OTP and one receipt job per payment. No cross-database foreign keys.", 55, 1250, 1780, 35, "subtitle")


# 05: Two-phase payment flow, including the transactional boundary and receipt job.
r = page(5, "Payment and OTP Flow", "05-payment-otp-flow", 1650, 1060,
         "Create records the full Tuition amount. Confirm is the only operation that debits the wallet.")
for cell_id, title, x, y, kind in [
    ("fl-lookup", "Log in and\nlook up tuition", 50, 220, "process"),
    ("fl-check", "Check UNPAID\nand balance", 360, 220, "decision"),
    ("fl-create", "Commit PENDING_OTP\nand hashed OTP", 670, 220, "process"),
    ("fl-email", "Send OTP email\nTTL 5 minutes", 980, 220, "process"),
    ("fl-enter", "Customer enters OTP", 1290, 220, "process"),
    ("fl-lock", "Lock payment + OTP\nvalidate single-use code", 1290, 600, "process"),
    ("fl-recheck", "Lock wallet + tuition\nrecheck status / balance", 980, 600, "decision"),
    ("fl-commit", "Atomic DB commit\ndebit · PAID · SUCCESS\nuse OTP · create receipt job", 670, 600, "success"),
    ("fl-job", "Send receipt email\nretry every 30 seconds", 360, 600, "process"),
    ("fl-done", "Payment complete", 50, 600, "success"),
]:
    box(r, cell_id, title, x, y, 260, 110, kind)
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
box(r, "fl-ineligible", "Already PAID or insufficient balance\n409 / 422; no payment created", 350, 430, 280, 80, "error")
box(r, "fl-mail-fail", "OTP delivery fails\n503; payment marked FAILED", 970, 430, 280, 80, "error")
box(r, "fl-otp-fail", "Invalid / expired OTP\n422; no debit", 1280, 825, 280, 85, "error")
box(r, "fl-finance-fail", "Already PAID / insufficient balance\n409 / 422; no debit", 945, 825, 300, 85, "error")
link(r, "fl-check-fail", "fl-check", "fl-ineligible", "reject", anchors(DASH, 0.5, 1, 0.5, 0))
link(r, "fl-email-fail", "fl-email", "fl-mail-fail", "SMTP failure", anchors(DASH, 0.5, 1, 0.5, 0))
link(r, "fl-otp-fail-edge", "fl-lock", "fl-otp-fail", "reject", anchors(DASH, 0.5, 1, 0.5, 0))
link(r, "fl-finance-fail-edge", "fl-recheck", "fl-finance-fail", "reject", anchors(DASH, 0.5, 1, 0.5, 0))
box(r, "fl-foot", "Database errors before commit roll back. Receipt failure leaves SUCCESS and a pending job; Notification uses a stable messageId for retries.", 55, 970, 1510, 40, "subtitle")


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
    save_xml(DOCS / f"{stem}-final.drawio", single)

print(MASTER)
for _, stem in pages:
    print(DOCS / f"{stem}-final.drawio")
