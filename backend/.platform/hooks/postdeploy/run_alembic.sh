# #!/bin/bash
# set -x
# source /var/app/venv/*/bin/activate
# cd /var/app/current
# echo ">>>>RDS_USERNAME=$RDS_USERNAME"
# echo ">>>>RDS_PASSWORD=$RDS_PASSWORD"
# echo ">>>>RDS_HOSTNAME=$RDS_HOSTNAME"
# echo ">>>>RDS_PORT=$RDS_PORT"
# echo ">>>>RDS_DB_NAME=$RDS_DB_NAME"
# ENCODED_USER=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${RDS_USERNAME}'))")
# ENCODED_PASSWORD=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${RDS_PASSWORD}'))")
# export DATABASE_URL="postgresql://${ENCODED_USER}:${ENCODED_PASSWORD}@${RDS_HOSTNAME}:${RDS_PORT}/${RDS_DB_NAME}"
# echo ">>>>DATABASE_URL=$DATABASE_URL"
# alembic -x db_url="$DATABASE_URL" upgrade head

#!/usr/bin/env bash
set -euo pipefail

# EB attaches RDS_* env vars when you create env w/ a database.
# Build DATABASE_URL if not already present.
if [[ -z "${DATABASE_URL:-}" ]] && [[ -n "${RDS_HOSTNAME:-}" ]]; then
  export DATABASE_URL="postgresql+psycopg://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_HOSTNAME}:${RDS_PORT}/${RDS_DB_NAME}"
fi

cd /var/app/current
. /var/app/venv/*/bin/activate
alembic upgrade head
echo "Alembic migration complete."