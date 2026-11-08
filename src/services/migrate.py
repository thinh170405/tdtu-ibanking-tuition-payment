import sys
from pathlib import Path

from sqlalchemy import create_engine, text


def migrate(service: str):
    if service == "account":
        from services.account.app import engine
    elif service == "notification":
        from services.notification.app import engine
    else:
        raise ValueError("service must be account or notification")
    migrations = sorted((Path(__file__).parent / service / "migrations").glob("*.sql"))
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(100) PRIMARY KEY)"))
        applied = {row[0] for row in connection.execute(text("SELECT version FROM schema_migrations"))}
        for migration in migrations:
            if migration.stem in applied:
                continue
            for statement in migration.read_text(encoding="utf-8").split(";"):
                if statement.strip():
                    connection.execute(text(statement.strip()))
            connection.execute(text("INSERT INTO schema_migrations (version) VALUES (:version)"), {"version": migration.stem})
    print(f"{service} migrations complete.")


if __name__ == "__main__":
    migrate(sys.argv[1])
