from pathlib import Path
import re

repo = Path(__file__).parent
legacy = (repo / 'templates/login.html').read_text(encoding='utf-8')
saas = (repo / 'templates/saas/login.html').read_text(encoding='utf-8')
base = (repo / 'templates/saas/base.html').read_text(encoding='utf-8')
css = (repo / 'static/css/auth_identity.css').read_text(encoding='utf-8')

assert 'css/auth_identity.css' in legacy
assert 'css/auth_identity.css' in base
assert 'block body_class' in base
assert 'saas-auth-page' in saas
assert 'name="username"' in legacy
assert 'name="password"' in legacy
assert 'name="email"' in saas
assert 'name="password"' in saas
assert 'url_for(\'auth.forgot_password\')' in legacy
assert 'url_for(\'auth.forgot_password\')' in saas
assert 'session' not in css
assert 'company_id' not in css
assert 'role' not in css
assert re.search(r'@media \(max-width: 760px\)', css)
print('shared auth stylesheet linked: OK')
print('legacy username/password form preserved: OK')
print('SaaS email/password form preserved: OK')
print('session and permission logic untouched by CSS: OK')
print('responsive mobile rules present: OK')
