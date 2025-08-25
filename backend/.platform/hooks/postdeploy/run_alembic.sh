#!/usr/bin/env bash
set -euo pipefail

# Navigate to the application directory
cd /var/app/current

# Load RDS environment variables properly
echo "Loading RDS configuration..."
# The correct way to export environment variables from get-config
export RDS_HOSTNAME=$(sudo /opt/elasticbeanstalk/bin/get-config environment -k RDS_HOSTNAME)
export RDS_PORT=$(sudo /opt/elasticbeanstalk/bin/get-config environment -k RDS_PORT)
export RDS_DB_NAME=$(sudo /opt/elasticbeanstalk/bin/get-config environment -k RDS_DB_NAME)
export RDS_USERNAME=$(sudo /opt/elasticbeanstalk/bin/get-config environment -k RDS_USERNAME)
export RDS_PASSWORD=$(sudo /opt/elasticbeanstalk/bin/get-config environment -k RDS_PASSWORD)

# Construct DATABASE_URL
if [[ -n "${RDS_HOSTNAME:-}" && -n "${RDS_PORT:-}" && -n "${RDS_DB_NAME:-}" && -n "${RDS_USERNAME:-}" && -n "${RDS_PASSWORD:-}" ]]; then
  export DATABASE_URL="postgresql://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_HOSTNAME}:${RDS_PORT}/${RDS_DB_NAME}"
  echo "DATABASE_URL constructed successfully (masked password)"
  echo "Connection string format: postgresql://username:******@hostname:port/dbname"
else
  echo "Error: RDS environment variables are not fully available." >&2
  echo "Available environment keys:"
  sudo /opt/elasticbeanstalk/bin/get-config environment-keys
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

# Debug information
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Alembic location: $(which alembic 2>/dev/null || echo 'not found')"

# Run Alembic migrations
echo "Running alembic upgrade head"
alembic upgrade head