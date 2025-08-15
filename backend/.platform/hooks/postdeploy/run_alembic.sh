#!/usr/bin/env bash
set -e

cd /var/app/current

# Ensure alembic.ini exists and has [alembic] section
cat > alembic.ini <<EOF
[alembic]
script_location = alembic
sqlalchemy.url = ${DATABASE_URL:-postgresql+psycopg2://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_HOSTNAME}:${RDS_PORT:-5432}/${RDS_DB_NAME}}
EOF

# Run migrations
alembic upgrade head