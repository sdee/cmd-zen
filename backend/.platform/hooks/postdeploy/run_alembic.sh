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
EOF

# Validate alembic.ini
if ! grep -q "[alembic]" alembic.ini; then
  echo "Error: alembic.ini is missing the [alembic] section header." >&2
  exit 1
fi

# Run migrations
alembic upgrade head