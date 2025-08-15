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

# Always write a clean, valid alembic.ini
cat > alembic.ini <<EOF
[alembic]
script_location = alembic
sqlalchemy.url = ${DATABASE_URL}
EOF

# Run migrations
alembic upgrade head