from pathlib import Path
import re

src = Path('templates/tracking.html').read_text(encoding='utf-8')
scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', src, flags=re.S)
inline = '\n'.join(scripts)
Path('/tmp/tracking_inline.js').write_text(inline, encoding='utf-8')
print(f'extracted {len(scripts)} inline scripts, {len(inline)} chars')

required = ['statusFilter', 'toggleTrails', 'exportGpsCsv', 'checkSpeedAlerts', 'trailPoints']
missing = [x for x in required if x not in inline]
if missing:
    raise SystemExit('missing: ' + ', '.join(missing))
print('gps feature markers: ok')
