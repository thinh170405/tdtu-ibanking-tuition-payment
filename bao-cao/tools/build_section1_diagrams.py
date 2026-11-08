"""Build the editable English UML and conceptual ERD for report section 1."""
from pathlib import Path
from xml.etree import ElementTree as E

OUT = Path(__file__).resolve().parents[1] / "docs"


def page(name, width, height):
    f = E.Element("mxfile", host="drawio", version="26.0.0", type="device")
    d = E.SubElement(f, "diagram", name=name, id=name.lower().replace(" ", "-"))
    m = E.SubElement(d, "mxGraphModel", dx=str(width), dy=str(height), grid="1", page="1", pageScale="1", pageWidth=str(width), pageHeight=str(height))
    r = E.SubElement(m, "root")
    E.SubElement(r, "mxCell", id="0")
    E.SubElement(r, "mxCell", id="1", parent="0")
    return f, r


def node(r, key, label, x, y, w, h, style, parent="1"):
    c = E.SubElement(r, "mxCell", id=key, value=label, style=style, vertex="1", parent=parent)
    E.SubElement(c, "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), attrib={"as": "geometry"})


def edge(r, key, src, dst, label="", dashed=False):
    style = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=#526B79;strokeWidth=2;endArrow=none;"
    if dashed:
        style += "dashed=1;endArrow=open;fontSize=13;labelBackgroundColor=#FFFFFF;"
    c = E.SubElement(r, "mxCell", id=key, value=label, style=style, edge="1", parent="1", source=src, target=dst)
    E.SubElement(c, "mxGeometry", relative="1", attrib={"as": "geometry"})


def save(f, name):
    E.indent(f, space="  ")
    E.ElementTree(f).write(OUT / name, encoding="utf-8", xml_declaration=True)


TITLE = "text;html=1;strokeColor=none;fillColor=none;fontFamily=Arial;fontSize=24;fontStyle=1;fontColor=#16364B;"
ACTOR = "shape=umlActor;html=1;verticalLabelPosition=bottom;verticalAlign=top;fontFamily=Arial;fontSize=15;"
UC = "ellipse;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=15;fillColor=#E7F2F8;strokeColor=#48758B;strokeWidth=2;"
BOX = "swimlane;startSize=38;html=1;container=1;collapsible=0;fontFamily=Arial;fontSize=17;fontStyle=1;fillColor=#F8FBFD;strokeColor=#8EAAB9;"

f, r = page("Tuition Payment Use Case", 1450, 920)
node(r, "title", "USE CASE DIAGRAM | IBANKING TUITION PAYMENT", 40, 20, 1300, 45, TITLE)
node(r, "system", "iBanking Tuition Payment Subsystem", 260, 100, 920, 750, BOX)
node(r, "user", "User / Customer", 65, 370, 110, 120, ACTOR)
node(r, "email", "Email Service", 1250, 370, 105, 120, ACTOR)
cases = [
    ("uc01", "UC01  Sign in", 80, 95),
    ("uc02", "UC02  View account and balance", 80, 205),
    ("uc03", "UC03  Look up student tuition", 80, 315),
    ("uc04", "UC04  Initiate full payment", 80, 425),
    ("uc05", "UC05  Verify email OTP", 80, 535),
    ("uc06", "UC06  Complete payment", 510, 535),
]
for key, label, x, y in cases:
    node(r, key, label, x, y, 330, 70, UC, parent="system")
for key in ("uc01", "uc02", "uc03", "uc04", "uc05"):
    edge(r, "user_" + key, "user", key)
edge(r, "mail_otp", "email", "uc04")
edge(r, "mail_confirmation", "email", "uc06")
edge(r, "include_lookup", "uc04", "uc03", "«include»")
edge(r, "extend_complete", "uc06", "uc05", "«extend» [valid OTP]", True)
node(r, "note", "UC06 starts after valid OTP. Database is an internal data store, not a UML actor.", 270, 865, 900, 30, TITLE.replace("fontSize=24", "fontSize=13").replace("fontStyle=1;", ""))
save(f, "01-phan-tich-nghiep-vu-use-case.drawio")

f, r = page("Initial Tuition Payment ERD", 1510, 900)
node(r, "title", "INITIAL ERD | IBANKING TUITION PAYMENT", 40, 20, 1300, 45, TITLE)
ENTITY = "swimlane;startSize=32;html=1;container=1;collapsible=0;fontFamily=Arial;fontSize=16;fontStyle=1;fillColor=#E3F0F7;strokeColor=#4C7890;strokeWidth=2;"
FIELDS = "text;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacingLeft=12;spacingTop=7;fontFamily=Arial;fontSize=14;strokeColor=none;fillColor=none;"
def entity(key, label, fields, x, y, h=245):
    node(r, key, label, x, y, 310, h, ENTITY)
    node(r, key + "_fields", "<br>".join(fields), 8, 35, 294, h-43, FIELDS, parent=key)
entity("users", "Users", ["PK user_id", "UQ username", "password_hash", "full_name, email, phone", "balance >= 0"], 45, 140)
entity("students", "Students", ["PK student_id (MSSV)", "full_name", "program"], 45, 510, 205)
entity("tuitions", "Tuitions", ["PK tuition_id", "FK student_id", "term", "amount > 0", "status, paid_at"], 565, 510)
entity("transactions", "Transactions", ["PK transaction_id", "FK user_id", "FK tuition_id", "UQ (user_id, request_id)", "amount, status", "created_at, completed_at"], 565, 140, 275)
entity("otps", "OTPs", ["PK otp_id", "FK/UQ transaction_id", "code_hash", "issued_at, expires_at", "used_at"], 1120, 140)
for key, src, dst, label in [
    ("u_tx", "users", "transactions", "1 to many"),
    ("s_tu", "students", "tuitions", "1 to many"),
    ("tu_tx", "tuitions", "transactions", "1 to many attempts"),
    ("tx_otp", "transactions", "otps", "1 to 0..1"),
]:
    edge(r, key, src, dst, label)
node(r, "note", "Only one SUCCESS transaction per tuition. OTP expires after 5 minutes and is used once. Cross-service references are logical links.", 55, 810, 1390, 45, TITLE.replace("fontSize=24", "fontSize=14").replace("fontStyle=1;", ""))
save(f, "01-phan-tich-nghiep-vu-erd.drawio")
