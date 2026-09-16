import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('ALLOW_SQLITE_FALLBACK', 'true')
os.environ.setdefault('SQLITE_PATH', str(PROJECT_ROOT / 'database.sqlite'))
os.environ.setdefault('SECRET_KEY', 'local-verification-only')
os.environ.setdefault('ADMIN_USERNAME', 'local-admin')
os.environ.setdefault('MASTER_PASSWORD', 'local-verification-only')

import app  # noqa: F401,E402
from sqlalchemy import inspect  # noqa: E402
from models.schema import InboundEmailTask  # noqa: E402

with app.app.app_context():
    table_exists = inspect(app.db.engine).has_table('erp_inbound_email_tasks')
    print(f'table_exists={table_exists}')
    rows = InboundEmailTask.query.count()
    print(f'initial_rows={rows}')
    if not table_exists:
        raise SystemExit('migration did not create erp_inbound_email_tasks')
