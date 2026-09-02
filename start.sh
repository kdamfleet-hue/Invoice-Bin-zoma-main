#!/bin/sh

export PORT="${PORT:-3000}"

# Database migrations (non-fatal if already applied)
flask db upgrade || echo "⚠️ Migration skipped or failed, continuing..."

exec gunicorn --workers 1 --threads 4 --worker-class gthread --timeout 120 \
--bind 0.0.0.0:${PORT} --access-logfile - --error-logfile - --log-level info app:app
