from app import app
client = app.test_client()
try:
    response = client.get('/')
    print("Response Status:", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
