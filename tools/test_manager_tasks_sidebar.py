import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('ALLOW_SQLITE_FALLBACK', 'true')
os.environ.setdefault('SQLITE_PATH', str(ROOT / 'database.sqlite'))
os.environ.setdefault('SECRET_KEY', 'local-sidebar-test')
os.environ.setdefault('ADMIN_USERNAME', 'local-admin')
os.environ.setdefault('MASTER_PASSWORD', 'local-sidebar-test')

import app  # noqa: E402
from flask import render_template  # noqa: E402

with app.app.test_request_context('/manager-tasks'):
    for role in ('admin', 'branch_manager', 'operations', 'viewer'):
        from flask import session
        session.clear()
        session['role'] = role
        html = render_template('base.html', is_admin=(role == 'admin'), active_branch='اختبار')
        visible = 'href="/manager-tasks"' in html
        print(f'{role}={visible}')
        assert visible is (role in {'admin', 'branch_manager', 'operations'})
print('✅ sidebar visibility test passed')
