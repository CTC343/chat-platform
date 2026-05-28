import urllib.request, json

data = json.dumps({"username": "admin", "password": "admin123456"}).encode()
req = urllib.request.Request(
    "http://127.0.0.1:9999/users/login",
    data=data,
    headers={"Content-Type": "application/json"}
)
try:
    resp = urllib.request.urlopen(req)
    print("Status:", resp.status)
    body = resp.read().decode()
    print("Response:", body[:200])
except Exception as e:
    print("Error:", e)
