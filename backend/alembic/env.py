import os
from sqlalchemy import engine_from_config, pool
from alembic import context
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pull connection URL from EB's default RDS_* environment variables
if os.getenv("RDS_HOSTNAME"):
    DB_USER = os.environ["RDS_USERNAME"]
    DB_PASS = os.environ["RDS_PASSWORD"]
    DB_HOST = os.environ["RDS_HOSTNAME"]
    DB_PORT = os.environ.get("RDS_PORT", "5432")
    DB_NAME = os.environ["RDS_DB_NAME"]
    db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # fallback to DATABASE_URL or local dev
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/mydb")

# Log the constructed db_url
logger.info(f"Using database URL: {db_url}")

# Alembic config object
config = context.config
config.set_main_option("sqlalchemy.url", db_url)