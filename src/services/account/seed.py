import json
import os
from pathlib import Path

from sqlalchemy import select

from services.account.app import SessionLocal, User, hasher
from services.migrate import migrate


def main():
    migrate("account")
    source_root = Path(__file__).resolve().parents[2]
    seed_path = source_root / "data" / "demo-base.json"
    source = json.loads(seed_path.read_text(encoding="utf-8"))
    extra_path = source_root / "data" / "demo-extra.json"
    if extra_path.exists():
        source["users"].extend(json.loads(extra_path.read_text(encoding="utf-8"))["users"])
    with SessionLocal.begin() as db:
        for row in source["users"]:
            existing = db.scalar(select(User).where(User.id == row["userId"]))
            suffix = row["userId"][1:]
            fallback_email = os.getenv("DEMO_EMAIL_1", row["email"]) if int(suffix) >= 3 else row["email"]
            email = os.getenv(f"DEMO_EMAIL_{suffix}", fallback_email)
            if existing:
                existing.email = email
                continue
            db.add(User(id=row["userId"], username=row["username"], password_hash=hasher.hash(row["passwordForSeeding"]), full_name=row["fullName"], phone=row["phone"], email=email))
    print("Account seed complete.")


if __name__ == "__main__":
    main()
