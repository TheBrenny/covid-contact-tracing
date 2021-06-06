import json
import requests

conv = {'phone_number': '+614xxxxxx',
        'latitude': 13.2,
        'longitude': 15.2,
        'code': 549660,
        'password': '87654321'}
s = json.dumps(conv)
#res = requests.post("http://127.0.0.1:5000/auth_request_code", json=s)

#res = requests.post("http://127.0.0.1:5000/auth_check_code", json=s)

res = requests.post("http://192.168.1.15:5000/data_entry", json=s)
print(str(res))