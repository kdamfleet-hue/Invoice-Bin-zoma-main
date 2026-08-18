import requests

s = requests.Session()
res = s.post('https://invoice-bin-zoma.509.rip/login', data={'username': 'Khaled@fleetadmin', 'password': 'Khaled@Damfleet1105090615'})
print('Login status:', res.status_code)

urls = [
    '/', '/oils', '/fuel', '/washing', '/handover', '/workshop', 
    '/inventory/tires', '/inventory/batteries', '/inventory/filters', 
    '/settings', '/dashboard', '/petty_cash', '/api/oils_data'
]

for u in urls:
    try:
        r = s.get(f'https://invoice-bin-zoma.509.rip{u}')
        print(f'{u}: {r.status_code}')
    except Exception as e:
        print(f'{u}: ERROR {e}')
