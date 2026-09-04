#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from urllib.parse import urljoin
import requests

BASE = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else 'https://invoice-bin-zoma.509.rip'
ROOT = Path(__file__).resolve().parents[1]
ROUTE_RE = re.compile(r"\.route\(\s*(['\"])(/[^'\"]*)\1(?:\s*,\s*methods\s*=\s*\[([^\]]*)\])?", re.M)
paths = set(['/'])
for source in [ROOT / 'app.py', *sorted((ROOT / 'routes').glob('*.py'))]:
    text = source.read_text(encoding='utf-8', errors='ignore')
    for _, raw, methods in ROUTE_RE.findall(text):
        # Safe GET probe only. Replace converters with conservative sample values.
        path = re.sub(r'<(?:int|float):[^>]+>', '1', raw)
        path = re.sub(r'<path:[^>]+>', 'test', path)
        path = re.sub(r'<[^>]+>', 'test', path)
        # Avoid duplicate variable routes that become the same probe.
        paths.add(path)

session = requests.Session()
session.headers.update({'User-Agent': 'Invoice-Bin-live-route-audit/1.0', 'Accept': 'text/html,application/json,*/*'})
rows = []
for path in sorted(paths):
    url = urljoin(BASE + '/', path.lstrip('/'))
    try:
        response = session.get(url, timeout=15, allow_redirects=False)
        location = response.headers.get('Location', '')
        rows.append((path, response.status_code, len(response.content), location[:120]))
    except Exception as exc:
        rows.append((path, 'ERR', 0, str(exc)[:120]))

print('base', BASE)
print('route_count', len(rows))
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
