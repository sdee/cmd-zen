#!/usr/bin/env python3
import os, sys, time, glob
from urllib.parse import quote_plus

# 1) Build DATABASE_URL from EB's attached RDS env if not provided
db_url = os.getenv("DATABASE_URL")
if not db_url and os.getenv("RDS_HOSTNAME"):
    user = os.getenv("RDS_USERNAME", "")
    pwd  = os.getenv("RDS_PASSWORD", "")
    host = os.getenv("RDS_HOSTNAME", "")
    port = os.getenv("RDS_PORT", "5432")
    name = os.getenv("RDS_DB_NAME", "ebdb")
    # psycopg3 driver
    db_url = f"postgresql+psycopg://{quote_plus(user)}:{quote_plus(pwd)}@{host}:{port}/{quote_plus(name)}"
    os.environ["DATABASE_URL"] = db_url

def mask(url: str) -> str:
    if not url: return "<empty>"
    return url.replace(os.getenv("RDS_PASSWORD",""), "******")

print("DATABASE_URL (masked):", mask(os.getenv("DATABASE_URL","")))

# 2) Ensure alembic & SQLAlchemy can import
try:
    from sqlalchemy import create_engine, text
except Exception as e:
    print("ERROR: SQLAlchemy not installed in EB venv?", e, file=sys.stderr)
    sys.exit(1)
try:
    from alembic.config import Config
    from alembic import command
except Exception as e:
    print("ERROR: Alembic not installed in EB venv?", e, file=sys.stderr)
    sys.exit(1)

# 3) Wait for DB to be reachable (first boots can lag)
engine = None
delay = 2
for attempt in range(1, 11):  # ~ up to ~ 6 min with backoff
    try:
        engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True, future=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"DB reachable on attempt {attempt}")
        break
    except Exception as e:
        print(f"DB not ready (attempt {attempt}): {e}", file=sys.stderr)
        time.sleep(delay)
        delay = min(delay * 1.5, 60)
else:
    print("ERROR: RDS never became reachable. Aborting migrations.", file=sys.stderr)
    sys.exit(1)

# 4) Run Alembic programmatically using /var/app/current
app_dir = "/var/app/current"
alembic_ini = os.path.join(app_dir, "alembic.ini")
if not os.path.exists(alembic_ini):
    print("ERROR: alembic.ini not found at", alembic_ini, file=sys.stderr)
    sys.exit(1)

cfg = Config(alembic_ini)
# Force URL here so Alembic doesn't rely on env.py guessing
cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

print("Running alembic upgrade head…")
try:
    command.upgrade(cfg, "head")
    print("Alembic migration complete.")
except Exception as e:
    print("ERROR: Alembic failed:", e, file=sys.stderr)
    sys.exit(1)