from app import app
for rule in app.url_map.iter_rules():
    if 'finance' in rule.endpoint or 'petty' in rule.rule:
        print(f'{rule.endpoint}: {rule.rule}')
