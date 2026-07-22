import urllib.request
try:
    response = urllib.request.urlopen("http://localhost:5000/finance/petty-cash")
    print(response.read().decode('utf-8')[:500])
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print(e.read().decode('utf-8'))
