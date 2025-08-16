# .platform/hooks/postdeploy/run_alembic.sh
#!/usr/bin/env bash
set -euo pipefail

# Navigate to the application directory
cd /var/app/current

# Validate DATABASE_URL
if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "Error: DATABASE_URL is not set." >&2
  exit 1
fi

# Activate the virtual environment
if [[ -f "/var/app/venv/staging-LQM1lest/bin/activate" ]]; then
  source /var/app/venv/staging-LQM1lest/bin/activate
else
  echo "Error: Virtual environment activation script not found." >&2
  exit 1
fi

# Run Alembic migrations
alembic upgrade head