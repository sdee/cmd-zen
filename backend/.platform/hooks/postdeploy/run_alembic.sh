# .platform/hooks/postdeploy/run_alembic.sh
#!/usr/bin/env bash
set -euo pipefail
cd /var/app/current

# Build DATABASE_URL from EB's RDS_* if it's not set
if [[ -z "${DATABASE_URL:-}" && -n "${RDS_HOSTNAME:-}" ]]; then
  export DATABASE_URL="postgresql+psycopg2://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_HOSTNAME}:${RDS_PORT:-5432}/${RDS_DB_NAME}"
fi

# Always write a clean, valid alembic.ini
printf "[alembic]\nscript_location = alembic\nsqlalchemy.url = %s\n" "${DATABASE_URL:-}" > alembic.ini

# Run migrations
alembic upgrade head