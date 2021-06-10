import requests

count = 0
while 1:
    count += 1
    print("Enter nurse password: ")
    password = input() #87654321
    res = requests.post("https://pfs-cct-demo.herokuapp.com/nurse_logon", json={'password': password})
    
    if 200 <= res.status_code < 300:
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
        print("Enter the phone number of the infected person in the format [04xxxxxxxx]")
        ph = input()
        res = requests.post("https://pfs-cct-demo.herokuapp.com/nurse_add_data", json={'phone_number': ph})
        print("\nAlerts sent, enter any key to return to menu")
        input()
    elif selection == '0':
        print("Goodbye")
        exit()
    else:
        print("Invalid user input")