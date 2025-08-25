from logging.config import fileConfig
import logging
import sys
import os
import traceback

from sqlalchemy import engine_from_config, pool, text
from alembic import context

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alembic.env")

# Add your project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

# Alembic Config object
config = context.config

# Override connection string with our db module
try:
    db_url = db._db_url()
    masked_url = db_url.split('@')[0].split(':')[0] + ":****@" + db_url.split('@')[1]
    logger.info(f"Using database URL: {masked_url}")
    config.set_main_option("sqlalchemy.url", db_url)
except Exception as e:
    logger.error(f"Error setting up database URL: {e}")
    traceback.print_exc()
    raise

# Interpret the config file for Python logging
if config.config_file_name is not None:
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

def check_db_state(connection, label=""):
    """Check database state"""
    try:
        logger.info(f"--- Database state {label} ---")
        
        # Check tables
        result = connection.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
        """))
        tables = [row[0] for row in result]
        logger.info(f"Tables: {tables}")
        
        # Check alembic_version
        if 'alembic_version' in tables:
            result = connection.execute(text("SELECT * FROM alembic_version"))
            versions = [row[0] for row in result]
            logger.info(f"Alembic version: {versions}")
    except Exception as e:
        logger.warning(f"Error checking database state: {e}")

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    try:
        # Use our engine directly to ensure proper connection
        engine = db.get_engine()
        
        with engine.connect() as connection:
            # Check DB state before migrations
            check_db_state(connection, "BEFORE migrations")
            
            # Configure context with connection
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                transaction_per_migration=True  # Isolate migrations in transactions
            )

            try:
                with context.begin_transaction():
                    context.run_migrations()
                logger.info("Migrations completed successfully")
            except Exception as e:
                logger.error(f"Error during migrations: {e}")
                traceback.print_exc()
                raise
            
            # Check DB state after migrations
            check_db_state(connection, "AFTER migrations")
            
    except Exception as e:
        logger.error(f"Failed to connect to database or run migrations: {e}")
        traceback.print_exc()
        raise

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()