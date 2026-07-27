#!/usr/bin/env bash
echo "=================================================="
echo "🚀 Bin Zoma Fleet - Production Startup"
echo "=================================================="

PORT="${PORT:-3000}"
WORKERS="${GUNICORN_WORKERS:-3}"
THREADS="${GUNICORN_THREADS:-2}"

echo "Port: $PORT | Workers: $WORKERS | Threads: $THREADS"

echo "⏳ Running database migrations..."
flask db upgrade 2>/dev/null || echo "ℹ️ Flask-Migrate skipped."

echo "🔥 Starting Gunicorn..."
exec gunicorn --workers "$WORKERS" --threads "$THREADS" --worker-class gthread --bind "0.0.0.0:$PORT" --timeout 120 --keep-alive 5 --access-logfile - --error-logfile - --log-level info app:app
