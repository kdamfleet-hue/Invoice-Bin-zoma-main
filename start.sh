#!/bin/bash

echo "⏳ Running database migrations..."
flask db upgrade || python -c "
from app import app, db
with app.app_context():
    try:
        db.create_all()
        print('Database tables created/verified successfully.')
    except Exception as e:
        print('Migration notice:', e)
" || true

echo "🚀 Starting Gunicorn server..."
exec gunicorn --workers 1 --threads 8 --bind 0.0.0.0:$PORT app:app
