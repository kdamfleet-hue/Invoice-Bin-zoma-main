import requests

s = requests.Session()
r_post = s.post('https://invoice-bin-zoma.509.rip/login', data={'username': 'Khaled@fleetadmin', 'password': 'Khaled@Damfleet1105090615'})
print('Login status:', r_post.status_code)

r_dash = s.get('https://invoice-bin-zoma.509.rip/')
print('GET / status:', r_dash.status_code)
if r_dash.status_code == 500:
    print('GET / 500 Error body:')
    print(r_dash.text[:2000])
