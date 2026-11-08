"""Build the editable UML use-case diagram for the tuition payment subsystem."""

from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, indent, tostring


OUT = Path(__file__).resolve().parents[1] / "docs" / "01-tuition-payment-use-case.drawio"


def cell(root, ident, label, style, x, y, w, h, parent="1"):
    item = SubElement(root, "mxCell", id=ident, value=label, style=style, vertex="1", parent=parent)
    SubElement(item, "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), as_="geometry")
    return item


def edge(root, ident, source, target, label="", style=""):
    item = SubElement(
        root, "mxCell", id=ident, value=label,
        style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
        + style,
        edge="1", parent="1", source=source, target=target,
    )
    SubElement(item, "mxGeometry", relative="1", as_="geometry")


def main():
    mxfile = Element("mxfile", host="drawio", version="26.0.0", type="device")
    diagram = SubElement(mxfile, "diagram", name="Tuition Payment Use Case", id="tuition-payment-use-case")
    model = SubElement(diagram, "mxGraphModel", dx="1600", dy="1100", grid="1", gridSize="10", guides="1", page="1", pageScale="1", pageWidth="1600", pageHeight="1100")
    root = SubElement(model, "root")
    SubElement(root, "mxCell", id="0")
    SubElement(root, "mxCell", id="1", parent="0")

    title = "text;html=1;convertToSvg=1;align=left;verticalAlign=middle;strokeColor=none;fillColor=none;fontFamily=Arial;"
    uc = "ellipse;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=16;fillColor=#E9F4FA;strokeColor=#31708E;strokeWidth=2;"
    internal = "ellipse;whiteSpace=wrap;html=1;convertToSvg=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=15;fillColor=#EDF7ED;strokeColor=#4E8B68;strokeWidth=2;"
    actor = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;convertToSvg=1;fontFamily=Arial;fontSize=15;fontColor=#173045;"
    assoc = "endArrow=none;strokeColor=#577080;strokeWidth=2;"
    include = "dashed=1;endArrow=open;strokeColor=#5E7180;strokeWidth=2;fontSize=13;fontFamily=Arial;labelBackgroundColor=#FFFFFF;"

    cell(root, "title", "USE CASE DIAGRAM | IBANKING TUITION PAYMENT", title + "fontSize=25;fontStyle=1;fontColor=#173045;", 35, 20, 1450, 48)
    cell(root, "subtitle", "Scope: sign in, look up tuition, pay the full amount from account balance, verify by email OTP, and view results.", title + "fontSize=14;fontColor=#506575;", 35, 73, 1450, 32)
    cell(root, "system", "iBanking Tuition Payment Subsystem", "swimlane;startSize=36;horizontal=1;html=1;convertToSvg=1;align=left;fontFamily=Arial;fontSize=17;fontStyle=1;fillColor=#F8FBFD;strokeColor=#8EAAB9;container=1;collapsible=0;", 265, 130, 1060, 820)
    cell(root, "payer", "iBanking User", actor, 80, 410, 90, 120)
    cell(root, "mail_provider", "Email Service", actor, 1400, 545, 90, 120)

    main_cases = [
        ("login", "UC01 · Sign in", 330, 185),
        ("profile", "UC02 · View profile and balance", 330, 300),
        ("lookup", "UC03 · Look up tuition", 330, 415),
        ("create", "UC04 · Create full-payment\ntransaction", 330, 530),
        ("confirm", "UC05 · Enter and verify OTP", 330, 655),
        ("history", "UC07 · View result and history", 330, 785),
    ]
    for ident, label, x, y in main_cases:
        cell(root, ident, label, uc, x - 265, y - 130, 310, 76, parent="system")
    cell(root, "send_otp", "Send OTP by email", internal, 620, 400, 290, 76, parent="system")
    cell(root, "complete", "UC06 · Complete payment", internal, 620, 525, 290, 76, parent="system")
    cell(root, "send_success", "Send payment confirmation", internal, 620, 655, 290, 76, parent="system")

    for ident, *_ in main_cases:
        edge(root, f"payer_{ident}", "payer", ident, style=assoc)
    edge(root, "mail_otp", "mail_provider", "send_otp", style=assoc)
    edge(root, "mail_success", "mail_provider", "send_success", style=assoc)
    edge(root, "create_otp", "create", "send_otp", "«include»", include)
    edge(root, "confirm_complete", "complete", "confirm", "«extend» [valid OTP]", include)
    edge(root, "complete_email", "send_success", "complete", "«extend» [payment succeeds]", include)

    cell(root, "note", "Rules: account registration is out of scope; partial payments are not allowed; payment completes only with a valid OTP and sufficient balance.",
         "rounded=1;whiteSpace=wrap;html=1;convertToSvg=1;align=left;spacingLeft=14;fontFamily=Arial;fontSize=13;fillColor=#FFF8E8;strokeColor=#D8B668;", 265, 980, 1060, 65)

    indent(mxfile, space="  ")
    content = tostring(mxfile, encoding="unicode").replace("as_=", "as=")
    OUT.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + content, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
