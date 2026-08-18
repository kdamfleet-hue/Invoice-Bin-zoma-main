import requests

r = requests.get('https://invoice-bin-zoma.509.rip/login')
print('GET /login status:', r.status_code)

r = requests.post('https://invoice-bin-zoma.509.rip/login', data={'username': 'Khaled@fleetadmin', 'password': 'Khaled@Damfleet1105090615'}, allow_redirects=False)
print('POST /login status:', r.status_code)
if r.status_code == 500:
    print('POST /login body:', r.text[:500])
