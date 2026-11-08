"""Build current and target iBanking microservices architecture diagrams."""

from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, indent, tostring


OUT = Path(__file__).resolve().parents[1] / "docs" / "02-microservices-architecture-clear.drawio"

TEXT = "text;html=1;convertToSvg=1;align=left;verticalAlign=middle;strokeColor=none;fillColor=none;fontFamily=Arial;"
CLIENT = "rounded=1;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=17;fillColor=#E9E1F4;strokeColor=#8067A4;strokeWidth=2;"
UI = "rounded=1;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=17;fillColor=#DDEEF7;strokeColor=#3C7997;strokeWidth=2;"
SERVICE = "rounded=1;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=17;fillColor=#DDEEF7;strokeColor=#3C7997;strokeWidth=2;"
MOCK = "rounded=1;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=17;fillColor=#FFF1CC;strokeColor=#B88D35;strokeWidth=2;"
DB = "shape=cylinder3;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=16;fillColor=#E3F1E2;strokeColor=#6A9A67;strokeWidth=2;"
EXT = "rounded=1;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=16;fillColor=#F1F1F1;strokeColor=#858585;strokeWidth=2;"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;endSize=8;strokeColor=#607D8B;strokeWidth=2;fontSize=13;fontFamily=Arial;labelBackgroundColor=#FFFFFF;"


def node(root, ident, label, x, y, w, h, style):
    c = SubElement(root, "mxCell", id=ident, value=label, style=style, vertex="1", parent="1")
    SubElement(c, "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), as_="geometry")


def edge(root, ident, a, b, label, extra=""):
    c = SubElement(root, "mxCell", id=ident, value=label, style=EDGE + extra, edge="1", parent="1", source=a, target=b)
    SubElement(c, "mxGeometry", relative="1", as_="geometry")


def page(mxfile, name, ident, subtitle, integrated):
    d = SubElement(mxfile, "diagram", name=name, id=ident)
    m = SubElement(d, "mxGraphModel", dx="1600", dy="1100", grid="1", gridSize="10", guides="1", page="1", pageScale="1", pageWidth="1600", pageHeight="1050")
    r = SubElement(m, "root")
    SubElement(r, "mxCell", id="0")
    SubElement(r, "mxCell", id="1", parent="0")
    node(r, "title", "MICROSERVICES ARCHITECTURE | " + ("TARGET INTEGRATION" if integrated else "CURRENT A STACK"), 40, 20, 1500, 52, TEXT + "fontSize=25;fontStyle=1;fontColor=#173045;")
    node(r, "subtitle", subtitle, 40, 76, 1500, 40, TEXT + "fontSize=14;fontColor=#506575;")
    node(r, "browser", "User browser", 50, 420, 220, 105, CLIENT)
    node(r, "frontend", "React frontend\n:5173", 355, 420, 260, 105, UI)
    node(r, "account", "Account Service\nFastAPI :8081\nLogin · profile · JWT", 740, 170, 290, 130, SERVICE)
    node(r, "account_db", "Account DB\nusers", 1190, 175, 290, 120, DB)
    node(r, "notification", "Notification Service\nFastAPI :8083\nOTP · receipt emails", 740, 740, 290, 130, SERVICE)
    node(r, "notification_db", "Notification DB\nemail_messages", 1190, 690, 290, 120, DB)
    node(r, "smtp", "External SMTP provider", 1190, 870, 290, 105, EXT)
    edge(r, "browser_frontend", "browser", "frontend", "HTTP local / HTTPS deployed")
    edge(r, "frontend_account", "frontend", "account", "REST · login / profile")
    edge(r, "account_db_edge", "account", "account_db", "SQL · owns users")
    edge(r, "notification_db_edge", "notification", "notification_db", "SQL · messageId / status")
    edge(r, "notification_smtp", "notification", "smtp", "SMTP · STARTTLS")
    if integrated:
        node(r, "payment", "Payment Service B\nFastAPI :8082\nWallet · tuition · OTP · transactions", 740, 425, 290, 150, SERVICE)
        node(r, "payment_db", "Payment DB\nwallets · students · tuitions\npayments · OTP · email jobs", 1190, 435, 290, 140, DB)
        edge(r, "frontend_payment", "frontend", "payment", "REST · Bearer JWT")
        edge(r, "payment_db_edge", "payment", "payment_db", "SQL · atomic payment")
        edge(r, "payment_notification", "payment", "notification", "internal REST · X-Internal-Key")
        node(r, "note", "Payment verifies the Account JWT locally. Financial updates are committed in Payment DB. Each service owns its data; no cross-database foreign keys.",
             350, 940, 750, 72, "rounded=1;whiteSpace=wrap;html=1;convertToSvg=1;align=left;spacingLeft=15;fontFamily=Arial;fontSize=14;fillColor=#FFF8E8;strokeColor=#D8B668;")
    else:
        node(r, "payment", "Payment mock\nFastAPI :8089\nFixed OTP 123456 · in-memory data", 740, 425, 290, 150, MOCK)
        edge(r, "frontend_payment", "frontend", "payment", "REST · Bearer JWT")
        node(r, "note", "Current Compose has PostgreSQL for Account and Notification. The Payment mock has no Payment DB and does not call Notification; UI payments do not send OTP email.",
             350, 940, 750, 72, "rounded=1;whiteSpace=wrap;html=1;convertToSvg=1;align=left;spacingLeft=15;fontFamily=Arial;fontSize=14;fillColor=#FFF8E8;strokeColor=#D8B668;")
    return d


def main():
    f = Element("mxfile", host="drawio", version="26.0.0", type="device")
    page(f, "01 Current A Stack", "current-a", "Implemented and running: Account, Notification, React UI, PostgreSQL and Payment mock.", False)
    page(f, "02 Target Integration", "target-integration", "Target after B delivers Payment Service. Its implementation and database schema must be verified against B's source.", True)
    indent(f, space="  ")
    OUT.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(f, encoding="unicode").replace("as_=", "as="), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
