#!/usr/bin/env bash
set -euo pipefail

# Navigate to the application directory
cd /var/app/current

# Load RDS environment variables
echo "Loading RDS configuration..."
eval "$(sudo /opt/elasticbeanstalk/bin/get-config environment -k RDS_HOSTNAME RDS_PORT RDS_DB_NAME RDS_USERNAME RDS_PASSWORD 2> /dev/null)"

# Construct DATABASE_URL
if [[ -n "${RDS_HOSTNAME:-}" && -n "${RDS_PORT:-}" && -n "${RDS_DB_NAME:-}" && -n "${RDS_USERNAME:-}" && -n "${RDS_PASSWORD:-}" ]]; then
  export DATABASE_URL="postgresql://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_HOSTNAME}:${RDS_PORT}/${RDS_DB_NAME}"
  echo "DATABASE_URL constructed successfully: ${DATABASE_URL}"
else
  echo "Error: RDS environment variables are not fully available." >&2
  echo "Available variables:"
  sudo /opt/elasticbeanstalk/bin/get-config environment | grep RDS
  exit 1
fi

# Find and activate the virtual environment dynamically
VENV_PATHS=(
  "/var/app/venv/staging-LQM1lest/bin/activate"
  "$(find /var/app/venv -name "activate" -type f | head -n 1)"
)

for VENV_PATH in "${VENV_PATHS[@]}"; do
  if [[ -f "$VENV_PATH" ]]; then
    echo "Activating virtual environment: $VENV_PATH"
    source "$VENV_PATH"
    VENV_ACTIVATED=true
    break
  fi
done

if [[ "${VENV_ACTIVATED:-}" != "true" ]]; then
  echo "Error: Virtual environment activation script not found." >&2
  exit 1
fi

# Run Alembic migrations
echo "Running alembic upgrade head with DATABASE_URL: ${DATABASE_URL}"
alembic upgrade head