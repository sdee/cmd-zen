#!/usr/bin/env python3
import os, subprocess, glob, sys

# Build DATABASE_URL from attached RDS env vars if not provided
if not os.getenv("DATABASE_URL") and os.getenv("RDS_HOSTNAME"):
    os.environ["DATABASE_URL"] = "postgresql+psycopg://{u}:{p}@{h}:{port}/{db}".format(
        u=os.environ.get("RDS_USERNAME",""),
        p=os.environ.get("RDS_PASSWORD",""),
        h=os.environ.get("RDS_HOSTNAME",""),
        port=os.environ.get("RDS_PORT","5432"),
        db=os.environ.get("RDS_DB_NAME",""),
    )

# Activate EB venv for subprocess by pointing to its python/alembic
venv = sorted(glob.glob("/var/app/venv/*/bin"))
if not venv:
    print("No EB venv found", file=sys.stderr)
    sys.exit(1)

alembic_bin = os.path.join(venv[-1], "alembic")
cwd = "/var/app/current"
print("Running alembic upgrade head...")
subprocess.check_call([alembic_bin, "upgrade", "head"], cwd=cwd)
print("Alembic migration complete.")
