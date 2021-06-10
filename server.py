import os
import threading
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import random
import math
from datetime import datetime, timedelta
import pymongo
from twilio.rest import Client
from flask import Flask
from flask import request
import flask
import json
import threading
import os
import time


########################################SMS FUNCTIONS##################################################################
def sendSMS(message_string, phone_number):
    client = Client('AC0f43a1dddccda0ae011e70bb1963621a', '4059bc1168b5b6adeae6de79b5d16fad')
    message = client.messages.create(body=message_string,from_='+12068232616',to=phone_number)

def sendSMSCode(phone_number, signature):
    phone_number = "+61{}".format(phone_number[1:])
    code = ''.join(["{}".format(random.randint(0, 9)) for _ in range(0, 6)])
    message = "<#> COVID Contact Tracing App\nVerifcation Code: {0}\n{1}".format(code, signature)
    sendSMS(message, phone_number)
    return code


def covidAlert(phone_number):
    message = "COVID Contact Tracing Alert!\n" \
        "You have been in close proximity with an active case of COVID-19. Self-isolate and get tested as soon as possible!"
    sendSMS(message, phone_number)

#########################################DB COMMANDS###################################################################
conn = pymongo.MongoClient(os.environ['DB_URL'])
def conDB():  # Creates a connection to the database
    db = conn.pfsdb
    return db


def register(phone_number):  # Adds registered user to the database
    encrypted = encrypt(phone_number)
    hashed = hash_string(phone_number)
    db = conDB()
    pDic = {"_id": hashed, "PhoneNumber": encrypted, "Hash": hashed, "Locations": []}
    db.users.insert_one(pDic)


def pingDB(phone_number, long, lat):  # Adds user location to the database
    hashed = hash_string(phone_number)
    current = datetime.now()
    date = datetime(current.year, current.month, current.day)
    db = conDB()
    query = {"Hash": hashed}
    inpvalues = {"$push": {"Locations": {"Long": long, "Lat": lat, "Date": date}}}
    db.users.update_one(query, inpvalues)


def declutterDB():  # Removes data from the DB that has existed for over two weeks
    current = datetime.now()
    datenow = datetime(current.year, current.month, current.day)
    d = timedelta(days=14)
    dcDate = datenow - d
    inpvalues = {"$pull": {"Locations": {"Date": {"$lte": dcDate}}}}
    db = conDB()
    db.users.update_many({}, inpvalues)
    time.sleep(86400)
    declutterDB()
    

def codeWrite(phone_number, code, signature): # Adds a code and signature to the DB separate from users
    hashed = hash_string(phone_number)
    db = conDB()
    ins = {
        "Hash": hashed,
        "Code": code,
        "Signature": signature
    }
    db.auth_codes.insert_one(ins)


def codeRead(phone_number, code, signature): # Finds and deletes the found authcode and signature for a given hash
    hashed = hash_string(phone_number)
    db = conDB()
    query = {
        "Hash": hashed,
        "Code": code,
        "Signature": signature
    }
    found = db.auth_codes.find_one_and_delete(query)
    print(found)
    return found != None


def covidLOC(phone_number):  # Creates array of covid affected locations and runs covidSystem
    hashed = hash_string(phone_number)
    db = conDB()
    filterLoc = {"_id": 0, "PhoneNumber": 0, "Hash": 0}
    locations = db.users.find_one({"Hash": hashed}, filterLoc)
    # locArray = []
    # for x in locations:
    #     for z in x["Locations"]:
    #         affected = [z["Long"], z["Lat"]]
    #         locArray.append(z.)
    covidSystem(locations["Locations"])


def covidSystem(locations):  # TODO Will alert all potentially affected people
    unencrypted = []
    db = conDB()
    for x in locations:
        range = getGeographicBox(x["Lat"], x["Long"])
        # longMax = {"Locations.Long": {"$lte": range[3]}}
        # longMin = {"Locations.Long": {"$gte": range[2]}}
        # latMax = {"Locations.Lat": {"$lte": range[1]}}
        # latMin = {"Locations.Lat": {"$gte": range[0]}}
        # andLong = {"$and": [longMax, longMin]}
        # andLat = {"$and": [latMax, latMin]}
        # inputCommand = {"$or": [andLong, andLat]}
        query = {
            "Locations": {
                "Lat": {
                    "$and": [
                        {"$gte": range["LatMin"]},
                        {"$lte": range["LatMax"]}
                    ]
                },
                "Long": {
                    "$and": [
                        {"$gte": range["LongMin"]},
                        {"$lte": range["LongMax"]}
                    ]
                }
            }
        }
        filterLoc = {"_id": 0, "Locations": 0, "Hash": 0}
        encrypted = db.users.find(query, filterLoc)
        for e in encrypted:
            tmp = decrypt(e["PhoneNumber"])
            unencrypted.append(tmp)
    unencrypted = list(set(unencrypted)) # removes duplicates
    # `unencrypted` at this point contains all the decrypted phone numbers
    for x in unencrypted:
        covidAlert(x)

########################################DISTANCE CALCULATION###########################################################
def getGeographicBox(lat, lon):#outputs a set of points that make up a square of side length 50m
    latmin = float(lat) - 0.225
    latmax = float(lat) + 0.225
    lonmin = float(lon) - (25/(111111*math.cos(math.radians(float(lat)))))
    lonmax = float(lon) + (25/(111111 * math.cos(math.radians(float(lat)))))
    range = {
        "LatMin": latmin,
        "LatMax": latmax,
        "LongMin": lonmin,
        "LongMax": lonmax
    }
    return range

###########################################ENCRYPTING AND HASHING######################################################
def encrypt(msg):
    return f.encrypt(str(msg).encode()).decode()


def decrypt(encrypted):
    return f.decrypt(encrypted).decode()


def hash_string(input): # intended to hash string passwords
    encoded_string = input.encode()
    hash_fn = hashlib.sha256()
    hash_fn.update(encoded_string)
    return hash_fn.hexdigest()


def hash_and_salt_string(input):
    salt = "FJNBTGEITVALPOEV"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt.encode('utf-8'), iterations=100
    )
    return base64.urlsafe_b64encode(kdf.derive(input.encode('utf-8')))


#############################################SERVER START UP###########################################################
count  = 0
while 1:
    print("Enter password: ")
    password = "12345678" #input() # remove input so heroku can use this
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
f = Fernet(key)

app = Flask(__name__)

#############################################HTTPS/Flask server methods###########################################################
@app.route('/data_entry', methods=['POST', 'GET'])
def data_entry():
    data = request.json
    phone_number = data['phone_number']
    longitude = data['lon']
    latitude = data['lat']
    pingDB(phone_number, longitude, latitude)
    print("{}, <{}, {}>".format(str(phone_number), str(latitude), str(longitude)))
    return flask.Response(status=201)


@app.route('/auth_request_code', methods=['POST'])
def auth_request_code():
    data = request.json
    phone_number = data['phone_number']
    signature = data['signature']
    code = sendSMSCode(phone_number, signature)
    codeWrite(phone_number, code, signature)
    print("{}: {} ({})".format(phone_number, code, signature))
    sent_msg = {'msg': "Text message has been sent"}
    return json.dumps(sent_msg)


@app.route('/auth_check_code', methods=['POST'])
def auth_check_code():
    data = request.json
    phone_number = data['phone_number']
    code = data['code']
    signature = data['signature']
    resp = codeRead(phone_number, code, signature)
    if(resp):
        print("codes match")
        register(phone_number)
        return flask.Response(status=204)
    else:
        return flask.Response(status=401)

@app.route('/nurse_logon', methods=['POST'])
def nurse_logon():
    data = request.json
    password = data['password']
    print(password)
    # this is simply the hash_string of 87654321, the current nurse password
    if(hash_string(password) == 'e24df920078c3dd4e7e8d2442f00e5c9ab2a231bb3918d65cc50906e49ecaef4'):
        print("nurse logon successful")
        return flask.Response(status=204)
    else:
        print("nurse logon failed")
        return flask.Response(status=401)



@app.route('/nurse_add_data', methods=['POST'])
def nurse_add_data():
    data = request.json
    phone_number = data['phone_number']
    covidLOC(phone_number)
    return flask.Response(status=204)

@app.route('/', methods=['GET'])
def home_page():
    return "Home page of the Covid Contact Tracing App that is indefinitely under development!"

class ScheduleThread(threading.Thread):
    def __init__(self, function):
        threading.Thread.__init__(self)
        self.runnable = function
        self.daemon = True

    def run(self):
        self.runnable()

thread = ScheduleThread(declutterDB)
thread.start()
app.run(host="0.0.0.0",port=os.environ["PORT"],debug=True)
