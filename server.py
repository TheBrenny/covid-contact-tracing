from os import system
import hashlib
import base64
import random
from twilio.rest import Client
import math
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timedelta
import pymongo
########################################SMS FUNCTIONS##################################################################
def sendSMS(message_string, phone_number):
    client = Client('AC0f43a1dddccda0ae011e70bb1963621a', '4059bc1168b5b6adeae6de79b5d16fad')
    message = client.messages \
        .create(body=message_string,from_='+12068232616',to=phone_number)

def sendSMSCode(phone_number):
    code = random.randint(100000, 999999)
    message = "Your authentication code for COVID-Contact-Tracing is: " + str(code)
    sendSMS(message, phone_number)
    return code

def covidAlert(phone_number):
    message = "You have been in close proximity with an active case of COVID-19." \
            "You need to get tested for COVID-19 as soon as possible"
    sendSMS(message, phone_number)
#######################################################################################################################

#########################################DB COMMANDS###################################################################


def conDB():  # Creates a connection to the database **ONLY WORKS ON LOCALHOST**
    conn = pymongo.MongoClient()
    db = conn.pfs
    return db


def register(phone_number):  # Adds registered user to the database
    encrypted = encrypt(phone_number, 123)  # 123 is proof of concept key
    db = conDB()
    pDic = {"PhoneNumber": encrypted, "LocDate": []}
    db.users.insertOne(pDic)  # SHOULD work


def pingDB(phone_number, long, lat):  # Pings user location to the database
    encrypted = encrypt(phone_number, 123)  # 123 is proof of concept key
    current = datetime.datetime.now()
    date = datetime.datetime(current.year, current.month, current.day)
    db = conDB()
    query = {"PhoneNumber": encrypted}
    inpvalues = {"$push": {"LocDate": {"Long": long, "Lat": lat, "Date": date}}}
    db.users.updateOne(query, inpvalues)


def declutterDB():  # Removes data from the DB that has existed for over two weeks
    current = datetime.datetime.now()
    datenow = datetime.datetime(current.year, current.month, current.day)
    d = datetime.timedelta(days=14)
    dcDate = datenow - d
    inpvalues = {"$pull": {"LocDate": {"LocDate.Date": {"$gte": dcDate}}}}
    multi = {"multi": True}
    db = conDB()
    db.users.updateMany({}, inpvalues, multi)


def covidLOC(phone_number):  # Creates array of covid affected locations. Runs covid system
    encrypted = encrypt(phone_number, 123)
    db = conDB()
    filterLoc = {"_id": 0, "PhoneNumber": 0}
    locations = db.users.find({"PhoneNumber": encrypted}, filterLoc).toArray()
    covidSystem(locations)


def covidSystem(locations):  # TBC Will alert all potentially affected people
    locations[0].Long
    locations[0].Lat  # TO BE COMPLETED


#######################################################################################################################

########################################DISTANCE CALCULATION###########################################################
def distance(lat1, lon1, lat2, lon2):#uses haversine formula, not convinced it works
    R = 6373
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def squareRange(lat, lon):#outputs a set of points that make up a square of side length 50m
    latmin = float(lat) - 0.225
    latmax = float(lat) + 0.225
    lonmin = float(lon) - (25/(111111*math.cos(math.radians(float(lat)))))
    lonmax = float(lon) + (25/(111111 * math.cos(math.radians(float(lat)))))
    range = [latmin, latmax, lonmin, lonmax]
    return range
#######################################################################################################################

###########################################ENCRYPTING AND HASHING######################################################
def encrypt(msg, key):
    msg = msg.encode()
    f = Fernet(key)
    encrypted = f.encrypt(msg)
    return encrypted

def decrypt(encrypted, key):
    f = Fernet(key)
    return f.decrypt(encrypted).decode()

def hash_string(input):#intended to hash string passwords
    encoded_string = input.encode()
    hash_fn = hashlib.sha256()
    hash_fn.update(encoded_string)
    return hash_fn.hexdigest()

def hash_and_salt_string(input):
    salt = "FJNBTGEITVALPOEV"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt.encode('utf-8'), iterations=100
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
#######################################################################################################################

#############################################SERVER START UP###########################################################
count  = 0
while 1:
    print("Enter password: ")
    password = input()
    # this is simply the hash_string of 12345678, the current admin password
    if(hash_string(password) == \
            'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f'):
        break
    else:
        print("access denied")
        count += 1
        if(count == 3):
            #sends sms notifcation to admin ph - dont uncomment until ready to deploy, wastes twilio credit
            #sendSMS("Someone is trying to login to the server", "+614XXXXXXXX")
            exit()

key = hash_and_salt_string(password)

#HTTPS SERVER INITIALISATION TO GO HERE
#######################################################################################################################

####################################TESTING INTERFACE##################################################################
while 1:
    print("\n\t0. Exit\n\t1. Test hash function\n\t2. Test Encryption and decryption" \
            "\n\t3. Test authentication code\n\t4. Test distance")
    selection = input()

    if selection == '1':
        print("\tInput a string to be hashed: ")
        string_input = input()
        print("\n\t SHA256 output: " + str(hash_string(string_input)))
        print("\nPress any key to return to menu")
        input()
    elif selection == '2':
        print("\tInput a string to be encrypted and decrypted: ")
        string_input = input()
        print("\t AES128 Encryption: " + str(encrypt(string_input,key)))
        print("\t AES128 Decryption: " + str(decrypt(encrypt(string_input,key),key)))
        print("\nPress any key to return to menu")
        input()
    elif selection == '3':
        print("\tInput a phone number in the format [+61][4xxxxxxxx] to test verification code")
        phone_number = input()

        #sendSMS(message, phone_number) #use this sparingly in testing, we know it works, dont waste twilio credit
        #read response from client, through https server
        #if(code == response):
        #    print("Authentication successful")
        #else:
        #    print("Authentication unsuccessful")
        print("Press any key to return to menu")
        input()
    elif selection == '4':
        #can use the below values for testing, distance should be 278.545589...
        #lat1 = 52.2296756
        #long1 = 21.0122287
        #lat2 = 52.406374
        #long2 = 16.9251681
        print("\tInput latitude 1")
        lat1 = float(input())
        print("\tInput latitude 2")
        lat2 = float(input())
        print("\tInput longitude 1")
        lon1 = float(input())
        print("\tInput longitude 2")
        lon2 = float(input())
        print("The distance between the two points is: " + str(distance(lat1, lon1, lat2, lon2)))
        print("\nPress any key to return to menu")
        input()
    elif selection == '0':
        print("Goodbye")
        exit()
    else:
        print("Invalid user input")
#######################################################################################################################