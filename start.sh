#!/bin/bash
set -e

echo "⏳ Running database migrations..."
flask db upgrade

echo "🚀 Starting Gunicorn server..."
exec gunicorn --workers 1 --threads 8 --bind 0.0.0.0:$PORT app:app
