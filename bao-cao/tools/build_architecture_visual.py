"""Create a presentation-style, editable microservices diagram."""

from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, indent, tostring


OUT = Path(__file__).resolve().parents[1] / "docs" / "02-microservices-architecture-visual.drawio"
INK = "#312267"
PURPLE = "#6742E8"
LINE = "#5B43AF"
PALE = "#D7DEFA"
WHITE = "#F8F7FF"


def node(root, ident, label, x, y, w, h, style, parent="1"):
    c = SubElement(root, "mxCell", id=ident, value=label, style=style, vertex="1", parent=parent)
    SubElement(c, "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), as_="geometry")


def edge(root, ident, source, target, label, dashed=False, **ports):
    style = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;endSize=10;"
    style += f"strokeColor={LINE};strokeWidth=2;fontColor={INK};fontSize=14;fontFamily=Arial;labelBackgroundColor={PALE};"
    if dashed:
        style += "dashed=1;dashPattern=7 5;"
    for key, value in ports.items():
        style += f"{key}={value};"
    c = SubElement(root, "mxCell", id=ident, value=label, style=style, edge="1", parent="1", source=source, target=target)
    SubElement(c, "mxGeometry", relative="1", as_="geometry")


def main():
    f = Element("mxfile", host="drawio", version="26.0.0", type="device")
    d = SubElement(f, "diagram", name="Microservices · Presentation Style", id="microservices-presentation")
    m = SubElement(d, "mxGraphModel", dx="1800", dy="1180", grid="1", gridSize="10", guides="1", page="1", pageScale="1", pageWidth="1800", pageHeight="1180")
    r = SubElement(m, "root")
    SubElement(r, "mxCell", id="0")
    SubElement(r, "mxCell", id="1", parent="0")

    text = f"text;html=1;convertToSvg=1;align=left;verticalAlign=middle;strokeColor=none;fillColor=none;fontFamily=Arial;fontColor={INK};"
    card = f"rounded=1;arcSize=16;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontColor={INK};fontSize=22;fillColor={WHITE};strokeColor=#8E79F5;strokeWidth=3;"
    badge = f"ellipse;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=25;fontStyle=1;fontColor=#FFFFFF;fillColor={PURPLE};strokeColor={PURPLE};strokeWidth=2;"
    db = f"shape=cylinder3;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontColor={INK};fontSize=17;fillColor=#E8E5FF;strokeColor=#8E79F5;strokeWidth=3;"
    border = f"rounded=1;arcSize=12;html=1;fillColor={PALE};strokeColor={LINE};strokeWidth=3;"

    m.set("background", PALE)
    node(r, "title", "Microservice architecture", 60, 55, 1250, 75, text + "fontSize=42;fontStyle=1;")
    node(r, "subtitle", "iBanking tuition payment  |  target integration with Payment Service B", 63, 135, 1400, 35, text + "fontSize=19;")

    # Browser-style interface card, visually mirroring the requested reference.
    node(r, "ui_frame", "", 670, 220, 460, 190, border)
    node(r, "ui_bar", "●  ●  ●       USER INTERFACE  ·  React :5173", 12, 7, 435, 38, text + "fontSize=19;fontStyle=1;", parent="ui_frame")
    node(r, "ui_line_1", "Login  ·  Profile  ·  Tuition lookup", 40, 62, 380, 42, f"rounded=1;html=1;convertToSvg=1;align=center;fontFamily=Arial;fontSize=18;fontColor={INK};fillColor=#EDF0FF;strokeColor=#9C8BFA;strokeWidth=2;", parent="ui_frame")
    node(r, "ui_line_2", "Payment  ·  OTP  ·  History", 40, 122, 380, 42, f"rounded=1;html=1;convertToSvg=1;align=center;fontFamily=Arial;fontSize=18;fontColor={INK};fillColor=#EDF0FF;strokeColor=#9C8BFA;strokeWidth=2;", parent="ui_frame")

    services = [
        ("account", "Account Service", "A", 150, "FastAPI :8081", "Login · profile · JWT"),
        ("payment", "Payment Service B", "P", 765, "FastAPI :8082", "Wallet · tuition · OTP · transactions"),
        ("notification", "Notification Service", "N", 1380, "FastAPI :8083", "OTP and receipt emails"),
    ]
    for ident, label, initial, x, port, responsibility in services:
        node(r, ident, "", x, 535, 300, 130, card + ("dashed=1;dashPattern=6 4;" if ident == "payment" else ""))
        node(r, ident + "_badge", initial, 112, 7, 76, 76, badge, parent=ident)
        node(r, ident + "_name", label, 10, 88, 280, 34, text + "align=center;fontSize=21;fontStyle=1;", parent=ident)
        node(r, ident + "_detail", port + "  |  " + responsibility, x - 20, 667, 340, 58, text + "align=center;whiteSpace=wrap;fontSize=16;")

    node(r, "account_db", "Account DB\nusers", 200, 790, 200, 135, db)
    node(r, "payment_db", "Payment DB\nwallets · students · tuition\npayments · OTP · email jobs", 815, 790, 200, 135, db)
    node(r, "notification_db", "Notification DB\nemail_messages", 1330, 790, 200, 135, db)
    node(r, "smtp", "SMTP provider", 1595, 825, 170, 70, f"rounded=1;whiteSpace=wrap;html=1;convertToSvg=1;align=center;fontFamily=Arial;fontSize=18;fontColor={INK};fillColor=#F3F0FF;strokeColor={LINE};strokeWidth=2;dashed=1;")

    edge(r, "ui_account", "ui_frame", "account", "REST · login/profile", dashed=True, exitX="0.15", exitY="1", entryX="0.5", entryY="0")
    edge(r, "ui_payment", "ui_frame", "payment", "REST · Bearer JWT", dashed=True, exitX="0.85", exitY="1", entryX="0.5", entryY="0")
    edge(r, "payment_notification", "payment", "notification", "internal REST · X-Internal-Key", exitX="1", exitY="0.5", entryX="0", entryY="0.5")
    edge(r, "account_store", "account", "account_db", "SQL", exitX="0.5", exitY="1", entryX="0.5", entryY="0")
    edge(r, "payment_store", "payment", "payment_db", "atomic SQL transaction", exitX="0.5", exitY="1", entryX="0.5", entryY="0")
    edge(r, "notification_store", "notification", "notification_db", "SQL", exitX="0.5", exitY="1", entryX="0.5", entryY="0")
    edge(r, "notification_smtp", "notification", "smtp", "SMTP · STARTTLS", dashed=True, exitX="1", exitY="1", entryX="0.5", entryY="0")

    node(r, "note", "Payment B is planned. Current A runs with an in-memory Payment mock on :8089; that mock does not send OTP email. Each real service owns its database.",
         70, 1040, 1190, 65, f"rounded=1;whiteSpace=wrap;html=1;convertToSvg=1;align=left;spacingLeft=14;fontFamily=Arial;fontSize=16;fontColor={INK};fillColor=#E9E6FF;strokeColor=#A392F0;strokeWidth=2;")

    indent(f, space="  ")
    OUT.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(f, encoding="unicode").replace("as_=", "as="), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
