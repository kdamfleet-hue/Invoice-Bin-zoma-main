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
from services.inbound_email import import_messages  # noqa: E402

message = {
    'message_id': 'manual-test-inbound-2026-09-17-001',
    'thread_id': 'manual-test-thread-001',
    'sender': 'trusted@example.com',
    'recipients': 'operations@example.com',
    'subject': 'اختبار رسالة واردة',
    'body_preview': 'هذه رسالة اختبار؛ يجب تحويلها إلى مهمة وارد.',
    'received_at': '2026-09-17T01:00:00+00:00',
}

with app.app.app_context():
    first = import_messages([message], branch_id=None)
    second = import_messages([message], branch_id=None)
    row = InboundEmailTask.query.filter_by(message_id=message['message_id']).one()
    print(f'first={first}')
    print(f'second={second}')
    print(f'row_status={row.status}')
    print(f'row_source={row.source}')
    print(f'row_subject={row.subject}')
    assert first == {'created': 1, 'skipped': 0, 'rejected': 0}
    assert second == {'created': 0, 'skipped': 1, 'rejected': 0}
    assert row.status == 'وارد'
    assert row.source == 'inbound_read_only'
    print('✅ inbound import and deduplication passed; no outbound mail path used')
