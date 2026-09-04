#!/bin/sh

export PORT="${PORT:-3000}"

# Database migrations. Kept NON-fatal on purpose: this platform replaces the running container
# on deploy, so refusing to start here would take the whole site down rather than just this
# deploy. The failure is made impossible to miss instead — and the two revisions that used to
# fail on every run (duplicate column adds) are now idempotent, so this should stay quiet.
if ! flask db upgrade; then
    echo "=================================================================="
    echo "❌ MIGRATION FAILED — the schema may be behind the code. Starting anyway"
    echo "   so the site stays up; fix the migration and redeploy. See the traceback above."
    echo "=================================================================="
fi

exec gunicorn --workers 1 --threads 4 --worker-class gthread --timeout 120 \
--bind 0.0.0.0:${PORT} --access-logfile - --error-logfile - --log-level info app:app
