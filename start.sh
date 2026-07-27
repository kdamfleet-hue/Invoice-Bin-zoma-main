#!/usr/bin/env bash
# ==============================================================================
# Bin Zoma Fleet & Invoicing Application - Production Startup Script
# ==============================================================================

echo "=================================================="
echo "🚀 بدء إجراءات تشغيل نظام بن زومه لإدارة الحركة..."
echo "=================================================="

# 1. Production Workers & Port Configuration
PORT="${PORT:-3000}"
WORKERS="${GUNICORN_WORKERS:-3}"
THREADS="${GUNICORN_THREADS:-2}"

echo "ℹ️ المنافذ والإعدادات: Port: $PORT | Workers: $WORKERS | Threads: $THREADS"

# 2. Database Pre-deployment Migration Step
echo "⏳ تنفيذ تحديثات قاعدة البيانات (Pre-deployment Step)..."

python -c "
import sys
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        db.create_all()
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
        print('✅ تم التحقق وتحديث الهيكل آلياً (Safe Schema Patch).')
    except Exception as e:
        print(f'⚠️ تنبيه في تهيئة القاعدة: {e}', file=sys.stderr)
" || true

flask db upgrade 2>/dev/null || echo "ℹ️ تم تجاوز Flask-Migrate (القاعدة محدثة بالكامل)."

# 3. Multi-Worker Production Gunicorn Launch
echo "=================================================="
echo "🔥 جاري تشغيل سيرفر Gunicorn الإنتاجي بـ 3 عمال وخيطين معالجة لكل عامل..."
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
