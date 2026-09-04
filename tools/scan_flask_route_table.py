#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from urllib.parse import urljoin
import requests

BASE = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else 'https://invoice-bin-zoma.509.rip'
TABLE = Path(sys.argv[2] if len(sys.argv) > 2 else '/tmp/flask_routes.txt')
paths = set(['/'])
for line in TABLE.read_text(encoding='utf-8', errors='ignore').splitlines():
    parts = line.split()
    if len(parts) < 3 or not parts[0] or not parts[2].startswith('/'):
        continue
    methods = parts[1]
    if 'GET' not in methods:
        continue
    path = parts[2]
    path = re.sub(r'<(?:int|float):[^>]+>', '1', path)
    path = re.sub(r'<path:[^>]+>', 'test', path)
    path = re.sub(r'<[^>]+>', 'test', path)
    paths.add(path)

s = requests.Session()
s.headers.update({'User-Agent': 'Invoice-Bin-live-route-audit/1.1', 'Accept': 'text/html,application/json,*/*'})
rows = []
for path in sorted(paths):
    try:
        r = s.get(urljoin(BASE + '/', path.lstrip('/')), timeout=15, allow_redirects=False)
        rows.append((path, r.status_code, len(r.content), r.headers.get('Location', '')[:120]))
    except Exception as e:
        rows.append((path, 'ERR', 0, str(e)[:120]))
print('base', BASE)
print('get_route_count', len(rows))
print('path\tstatus\tbytes\tlocation_or_error')
for row in rows:
    print('\t'.join(map(str, row)))
print('\nsummary')
for label, predicate in [
    ('5xx', lambda s: isinstance(s, int) and s >= 500),
    ('4xx', lambda s: isinstance(s, int) and 400 <= s < 500),
    ('redirect', lambda s: isinstance(s, int) and 300 <= s < 400),
    ('2xx', lambda s: isinstance(s, int) and 200 <= s < 300),
    ('error', lambda s: s == 'ERR'),
]:
    print(label, sum(predicate(r[1]) for r in rows))
