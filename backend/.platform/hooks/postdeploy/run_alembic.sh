#!/usr/bin/env bash
set -euo pipefail
source /var/app/venv/*/bin/activate
cd /var/app/current
alembic upgrade head