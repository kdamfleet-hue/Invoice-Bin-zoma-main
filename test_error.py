from app import app
app.config['TESTING'] = True
app.config['DEBUG'] = True
client = app.test_client()
try:
    client.post('/login', data={'username': 'Khaled@fleetadmin', 'password': 'Khaled@Damfleet1105090615'})
    res = client.get('/', follow_redirects=True)
    if res.status_code == 500:
        print("ERROR 500")
        print(res.get_data(as_text=True)[:2000])
    else:
        print("STATUS:", res.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
