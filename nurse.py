import json
import requests

#if we cant get boolean response back from the server uncomment
def hash_string(input):
    encoded_string = input.encode()
    hash_fn = hashlib.sha256()
    hash_fn.update(encoded_string)
    return hash_fn.hexdigest()

count  = 0
while 1:
    count += 1
    print("Enter nurse password: ")
    password = input() #87654321
    password_dict = {'password': '87654321'}
    password_json = json.dumps(password_dict)
    res = requests.post("http://192.168.1.15:5000/nurse_logon", json=password_json)

    if "201" in str(res):
        logon = False
    else:
        logon = False
    if (logon == True):
        print("nurse logon successful")
        break
    else:
        print("access denied")
        count += 1
        if (count == 3):
            exit()
 # if we cant get boolean response back from the server uncomment
   #if (hash_string(password) == \
   #         'e24df920078c3dd4e7e8d2442f00e5c9ab2a231bb3918d65cc50906e49ecaef4'):
   #     print("nurse logon successful")

   #     break
    #else:
     #   print("access denied")
      #  count += 1
       # if(count == 3):
        #    exit()

#enter ph# into server to alert users


