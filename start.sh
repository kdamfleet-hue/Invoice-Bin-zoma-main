#!/bin/sh

# 1. Database migrations
flask db upgrade || echo "⚠️ Migration skipped or failed, continuing..."

# 2. Production Gunicorn: 9 concurrent handlers (3 workers x 3 threads) + memory recycling
exec gunicorn --workers 3 --threads 3 --worker-class gthread --timeout 120 --max-requests 1000 --max-requests-jitter 50 --keep-alive 5 --bind 0.0.0.0:${PORT:-5000} --access-logfile - --error-logfile - --log-level info app:app
