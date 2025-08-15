# .platform/hooks/postdeploy/run_alembic.sh
#!/usr/bin/env bash
set -euo pipefail
cd /var/app/current

# Build DATABASE_URL from EB's RDS_* if it's not set
if [[ -z "${DATABASE_URL:-}" && -n "${RDS_HOSTNAME:-}" ]]; then
  export DATABASE_URL="postgresql+psycopg2://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_HOSTNAME}:${RDS_PORT:-5432}/${RDS_DB_NAME}"
fi

# Validate DATABASE_URL
if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "Error: DATABASE_URL is not set or invalid." >&2
  exit 1
fi

# Log DATABASE_URL for debugging
echo "Using DATABASE_URL: ${DATABASE_URL}"

# Always write a clean, valid alembic.ini
cat > alembic.ini <<EOF
[alembic]
script_location = alembic
sqlalchemy.url = ${DATABASE_URL}

[loggers]
keys = root,sqlalchemy,alembic
[handlers]
keys = console
[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine
[logger_alembic]
level = INFO
handlers = console
qualname = alembic
[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic
[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF

# Activate the virtual environment
if [[ -f "/var/app/venv/staging-LQM1lest/bin/activate" ]]; then
  source /var/app/venv/staging-LQM1lest/bin/activate
else
  echo "Error: Virtual environment activation script not found." >&2
  exit 1
fi

# Check if Alembic is installed
if ! command -v alembic &> /dev/null; then
  echo "Error: alembic command not found. Ensure Alembic is installed in the virtual environment." >&2
  exit 1
fi

# Validate alembic.ini
if ! grep -q "[alembic]" alembic.ini; then
  echo "Error: alembic.ini is missing the [alembic] section header." >&2
  exit 1
fi

# Log alembic.ini content for debugging
echo "Generated alembic.ini content:" >&2
cat alembic.ini >&2

# Run migrations
alembic upgrade head