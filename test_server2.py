import urllib.request
try:
    response = urllib.request.urlopen("http://localhost:5000/finance/petty-cash", timeout=5)
    print(response.read().decode('utf-8')[:500])
except Exception as e:
    print(f"Error: {e}")
