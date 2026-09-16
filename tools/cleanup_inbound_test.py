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

import app  # noqa: E402
from models.schema import InboundEmailTask  # noqa: E402

with app.app.app_context():
    deleted = InboundEmailTask.query.filter_by(message_id='manual-test-inbound-2026-09-17-001').delete()
    from models.schema import db
    db.session.commit()
    print(f'deleted_test_rows={deleted}')
    print(f'remaining_rows={InboundEmailTask.query.count()}')
