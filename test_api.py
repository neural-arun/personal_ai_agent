import urllib.request
import json

data = json.dumps({"message": "Testing telegram push", "session_id": "api_test"}).encode("utf-8")
req = urllib.request.Request("http://localhost:8002/chat", data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as f:
    print(f.read().decode("utf-8"))
