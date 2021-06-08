import json
import requests

count = 0
while 1:
    count += 1
    print("Enter nurse password: ")
    password = input() #87654321
    password_dict = {'password': password}
    password_json = json.dumps(password_dict)
    res = requests.post("https://pfs-cct-demo.herokuapp.com/nurse_logon", json=password_json)

    print(str(res))
    if "201" in str(res):
        print("nurse logon successful")
        break
    else:
        print("access denied")
        if (count >= 3):
            exit()

while 1:
    print("\n\t1. Alert potentially infected users to nearby COVID case\n\t0. Exit")
    selection = input()
    if selection == '1':
        print("Enter the phone number of the infected person in the format [+614xxxxxxxx]")
        ph = input()
        ph_dict = {'phone_number': ph}
        ph_json = json.dumps(ph_dict)
        res = requests.post("https://pfs-cct-demo.herokuapp.com/nurse_add_data", json=ph_dict)
        print(ph_json)
        print("\nAlerts sent, enter any key to return to menu")
        input()
    elif selection == '0':
        print("Goodbye")
        exit()
    else:
        print("Invalid user input")