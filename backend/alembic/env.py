from logging.config import fileConfig
import logging
import sys
import os

from sqlalchemy import engine_from_config, create_engine, pool, text
from alembic import context

# Set up custom logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alembic.env")

# Import your db module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

# this is the Alembic Config object
config = context.config

# Get database URL from our db.py
db_url = db._db_url()
sanitized_url = db_url.split("@")[0].split(":")
sanitized_url = f"{sanitized_url[0]}:{sanitized_url[1]}:******@" + db_url.split("@")[1]
logger.info(f"Using database URL: {sanitized_url}")
config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# Set target metadata to None (we're using SQL in migrations not models)
target_metadata = None

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def check_database_state(connection, title):
    """Check database tables and log them"""
    try:
        logger.info(f"--- {title} ---")
        # Check tables
        result = connection.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
        """))
        tables = [row[0] for row in result]
        if tables:
            logger.info(f"Tables: {', '.join(tables)}")
        else:
            logger.info("No tables found")
            
        # Check alembic_version
        if 'alembic_version' in tables:
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            versions = [row[0] for row in result]
            logger.info(f"Alembic versions: {', '.join(versions)}")
        else:
            logger.info("No alembic_version table")
    except Exception as e:
        logger.error(f"Error checking database state: {e}")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Create our own engine directly
    try:
        engine = db.get_engine()
        
        with engine.connect() as connection:
            check_database_state(connection, "Database state BEFORE migrations")
            
            # Configure alembic context
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                transaction_per_migration=True  # Important to isolate migrations
            )
            
            # Run migrations
            logger.info("Running migrations...")
            with context.begin_transaction():
                context.run_migrations()
            
            check_database_state(connection, "Database state AFTER migrations")
    except Exception as e:
        logger.error(f"Error during migration: {e}", exc_info=True)
        raise


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
