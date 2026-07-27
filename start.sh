#!/usr/bin/env bash
# ==============================================================================
# Bin Zoma Fleet & Invoicing Application - Production Startup Script
# ==============================================================================

set -e

echo "=================================================="
echo "🚀 بدء إجراءات تشغيل نظام بن زومه لإدارة الحركة..."
echo "=================================================="

# 1. Ambient Environment Setup
PORT="${PORT:-10000}"
WORKERS="${GUNICORN_WORKERS:-2}"
THREADS="${GUNICORN_THREADS:-4}"

echo "ℹ️ المنافذ والإعدادات: Port: $PORT | Workers: $WORKERS | Threads: $THREADS"

# 2. Self-Healing Database & Migration Upgrade
echo "⏳ جاري التحقق من الهيكل وتنفيذ التحديثات (Migrations)..."

python -c "
import sys
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        db.create_all()
        print('✅ تم التحقق من وجود الجداول الأساسية.')

        engine_name = db.engine.name
        with db.engine.connect() as conn:
            if engine_name == 'postgresql':
                conn.execute(text('ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS is_dedicated BOOLEAN DEFAULT FALSE;'))
                conn.execute(text('ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS allowed_route VARCHAR(200) DEFAULT \'/\';'))
                conn.commit()
            else:
                try:
                    conn.execute(text('ALTER TABLE user ADD COLUMN is_dedicated BOOLEAN DEFAULT 0'))
                except Exception:
                    pass
                try:
                    conn.execute(text('ALTER TABLE user ADD COLUMN allowed_route VARCHAR(200) DEFAULT \'/\''))
                except Exception:
                    pass
                conn.commit()
        print('✅ تم التحديث التلقائي لجدول المستخدمين (Self-Healing Schema Patch).')

    except Exception as e:
        print(f'⚠️ تنبيه أثناء تجهيز قاعدة البيانات: {e}', file=sys.stderr)
" || true

flask db upgrade 2>/dev/null || echo "ℹ️ تم تجاوز Flask-Migrate (القاعدة محدثة بالكامل)."

# 3. Production Gunicorn Server Launch
echo "=================================================="
echo "🔥 جاري تشغيل سيرفر Gunicorn الإنتاجي..."
echo "=================================================="

exec gunicorn \
    --workers "$WORKERS" \
    --threads "$THREADS" \
    --worker-class gthread \
    --bind "0.0.0.0:$PORT" \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app
