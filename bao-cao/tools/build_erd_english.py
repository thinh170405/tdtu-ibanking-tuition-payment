"""Create an English editable ERD from the reviewed project ERD."""

from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1] / "docs"
SOURCE = ROOT / "03-erd.drawio"
OUTPUT = ROOT / "03-tuition-payment-erd.drawio"

LABELS = {
    "er_title": "ERD | IBANKING TUITION PAYMENT",
    "er_note": "Account and Notification tables are implemented. Payment B is a proposed logical model; align table names, columns and constraints with B's migrations when its source is available.",
    "users": "users [Account DB]",
    "wallets": "wallets [Payment DB]",
    "students": "students [Payment DB]",
    "messages": "email_messages [Notification DB]",
    "otps": "otp_challenges [Payment DB]",
    "payments": "payments [Payment DB]",
    "tuitions": "tuitions [Payment DB]",
    "jobs": "email_jobs [Payment DB]",
    "users_fields": "PK id\nUQ username\npassword_hash\nfull_name\nphone\nemail",
    "wallets_fields": "PK user_id (Account reference)\nbalance ≥ 0\ncurrency",
    "students_fields": "PK student_id (8-digit ID)\nstudent_name",
    "messages_fields": "PK message_id\npayload_hash\nstatus\nupdated_at",
    "otps_fields": "PK otp_id\nFK payment_id\ncode_hash\nexpires_at\nused_at",
    "payments_fields": "PK payment_id\nuser_id (Account reference)\nFK tuition_id\nrequest_id (UQ with user_id)\namount · status · timestamps",
    "tuitions_fields": "PK tuition_id\nFK student_id\namount > 0\nstatus · paid_at",
    "jobs_fields": "PK job_id\nFK payment_id\nmessage_id (API reference)\ntype · status · retry_at",
    "er1": "1 : 1 · user_id",
    "er2": "1 : many · user_id",
    "er3": "1 : many",
    "er4": "1 : many",
    "er5": "1 : many attempts",
    "er6": "1 : 1",
    "er7": "1 : many",
    "er8": "message_id · API, no FK",
    "er_legend": "Dashed lines represent cross-service references, not database foreign keys. Payment DB must allow at most one successful payment per tuition item.",
}


def main():
    tree = ET.parse(SOURCE)
    diagram = tree.getroot().find("diagram")
    diagram.set("name", "Tuition Payment ERD")
    diagram.set("id", "tuition-payment-erd")
    for cell in diagram.findall(".//mxCell"):
        if cell.get("id") in LABELS:
            cell.set("value", LABELS[cell.get("id")])
    ET.indent(tree, space="  ")
    tree.write(OUTPUT, encoding="utf-8", xml_declaration=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
