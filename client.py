import json
import requests

conv = {'phone_number': '+614xxxxxx',
        'lat': 13.2,
        'lon': 15.2,
        'code': 549660,
        'password': '87654321'}
s = json.dumps(conv)
#res = requests.post("https://pfs-cct-demo.herokuapp.com/auth_request_code", json=s)

#res = requests.post("https://pfs-cct-demo.herokuapp.com/auth_check_code", json=s)

res = requests.post("https://pfs-cct-demo.herokuapp.com/nurse_logon", json=s)#change to https when running within heroko
print(str(res))