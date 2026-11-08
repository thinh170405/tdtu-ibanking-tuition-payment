import json
import os
from pathlib import Path

from sqlalchemy import select

from services.account.app import SessionLocal, User, hasher
from services.migrate import migrate


def main():
    migrate("account")
    source_root = Path(__file__).resolve().parents[2]
    candidates = [source_root / "contract", source_root.parent / "cau-hinh-chung" / "contract"]
    seed_path = next((path for folder in candidates if folder.exists() for path in folder.rglob("02-du-lieu-mau.json")), None)
    if seed_path is None:
        raise FileNotFoundError("Không tìm thấy 02-du-lieu-mau.json trong cau-hinh-chung/contract")
    source = json.loads(seed_path.read_text(encoding="utf-8"))
    with SessionLocal.begin() as db:
        for row in source["users"]:
            existing = db.scalar(select(User).where(User.id == row["userId"]))
            email = os.getenv(f"DEMO_EMAIL_{row['userId'][1:]}", row["email"])
            if existing:
                existing.email = email
                continue
            db.add(User(id=row["userId"], username=row["username"], password_hash=hasher.hash(row["passwordForSeeding"]), full_name=row["fullName"], phone=row["phone"], email=email))
    print("Account seed complete.")


if __name__ == "__main__":
    main()
