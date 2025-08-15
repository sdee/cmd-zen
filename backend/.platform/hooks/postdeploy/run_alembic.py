import os, sys, time
from urllib.parse import quote_plus

# flush logs line-by-line
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Build DATABASE_URL from attached RDS env if not provided
db_url = os.getenv("DATABASE_URL")
if not db_url and os.getenv("RDS_HOSTNAME"):
    user = os.getenv("RDS_USERNAME", "")
    pwd  = os.getenv("RDS_PASSWORD", "")
    host = os.getenv("RDS_HOSTNAME", "")
    port = os.getenv("RDS_PORT", "5432")
    name = os.getenv("RDS_DB_NAME", "ebdb")
    db_url = f"postgresql+psycopg2://{quote_plus(user)}:{quote_plus(pwd)}@{host}:{port}/{quote_plus(name)}" 
    os.environ["DATABASE_URL"] = db_url

print("Postdeploy: using DB URL (masked):", (db_url or "<empty>").replace(os.getenv("RDS_PASSWORD",""), "******"))

# Import deps
try:
    from sqlalchemy import create_engine, text
    from alembic.config import Config
    from alembic import command
except Exception as e:
    print("ERROR: missing dependencies in EB venv (sqlalchemy/alembic/psycopg).", e, file=sys.stderr)
    sys.exit(1)

# Wait for DB to be reachable (fresh RDS can lag)
delay = 2
for attempt in range(1, 11):
    try:
        engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True, future=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"DB reachable on attempt {attempt}")
        break
    except Exception as e:
        print(f"DB not ready (attempt {attempt}): {e}", file=sys.stderr)
        time.sleep(delay)
        delay = min(int(delay * 1.5), 60)
else:
    print("ERROR: RDS never became reachable; aborting migrations.", file=sys.stderr)
    sys.exit(1)

# Run Alembic programmatically, forcing the URL so localhost isn't used
app_dir = "/var/app/current"
alembic_ini = os.path.join(app_dir, "alembic.ini")
if not os.path.exists(alembic_ini):
    print("ERROR: alembic.ini not found at", alembic_ini, file=sys.stderr)
    sys.exit(1)

cfg = Config(alembic_ini)
cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

print("Running alembic upgrade head…")
try:
    command.upgrade(cfg, "head")
    print("Alembic migration complete.")
except Exception as e:
    print("ERROR: Alembic failed:", e, file=sys.stderr)
    sys.exit(1)