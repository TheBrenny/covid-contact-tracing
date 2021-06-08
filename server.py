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
from flask import jsonify
import flask
import json
import threading
import os
import time


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

#########################################DB COMMANDS###################################################################
def conDB():  # Creates a connection to the database **ONLY WORKS ON LOCALHOST**
    conn = pymongo.MongoClient()
    db = conn.pfs
    return db


def register(phone_number):  # Adds registered user to the database
    encrypted = encrypt(phone_number)
    hashed = hash_string(phone_number)
    db = conDB()
    pDic = {"PhoneNumber": encrypted, "Hash": hashed, "LocDate": []}
    db.users.insert_one(pDic)


def pingDB(phone_number, long, lat):  # Pings user location to the database
    hashed = hash_string(phone_number)
    current = datetime.now()
    date = datetime(current.year, current.month, current.day)
    db = conDB()
    query = {"Hash": hashed}
    inpvalues = {"$push": {"LocDate": {"Long": long, "Lat": lat, "Date": date}}}
    db.users.update_one(query, inpvalues)


def declutterDB():  # Removes data from the DB that has existed for over two weeks
    current = datetime.now()
    datenow = datetime(current.year, current.month, current.day)
    d = timedelta(days=14)
    dcDate = datenow - d
    inpvalues = {"$pull": {"LocDate": {"LocDate.Date": {"$gte": dcDate}}}}
    db = conDB()
    db.users.update_many({}, inpvalues)
    time.sleep(86400)
    declutterDB()
    

def codeWrite(phone_number, code, signature):
    hashed = hash_string(phone_number)
    db = conDB()
    query = {"Hash": hashed}
    inpvalues = {"$set": {"Code": code}}
    db.users.update_one(query, inpvalues)
    inpvalues = {"$set": {"Signature": signature}}
    db.users.update_one(query, inpvalues)


def codeRead(phone_number):
    hashed = hash_string(phone_number)
    db = conDB()
    query = {"Hash": hashed}
    filterLoc = {"_id": 0, "PhoneNumber": 0, "Hash": 0, "LocDate": 0}
    code = db.users.find(query, filterLoc)
    fCode = ""
    signature = ""
    for x in code:
        if 'Code' in x:
            fCode = x["Code"]
            signature = x["Signature"]
    inpvalues = {"$unset": {"Code": ""}}
    db.users.update_one(query, inpvalues)
    inpvalues = {"$unset": {"Signature": ""}}
    db.users.update_one(query, inpvalues)
    out = {'fCode': fCode, 'signature': signature}
    return out


def covidLOC(phone_number):  # Creates array of covid affected locations. Runs covid system
    hashed = hash_string(phone_number)
    db = conDB()
    filterLoc = {"_id": 0, "PhoneNumber": 0, "Hash": 0}
    locations = db.users.find({"Hash": hashed}, filterLoc)
    locArray = []
    for x in locations:
        for z in x["LocDate"]:
            affected = [z["Long"], z["Lat"]]
            locArray.append(affected)
    covidSystem(locArray)


def covidSystem(locations):  # TBC Will alert all potentially affected people
    unencrypted = []
    for x in locations:
        range = squareRange(x[1], x[0])
        longMax = {"LocDate.Long": {"$lte": range[3]}}
        longMin = {"LocDate.Long": {"$gte": range[2]}}
        latMax = {"LocDate.Lat": {"$lte": range[1]}}
        latMin = {"LocDate.Lat": {"$gte": range[0]}}
        andLong = {"$and": [longMax, longMin]}
        andLat = {"$and": [latMax, latMin]}
        inputCommand = {"$or": [andLong, andLat]}
        filterLoc = {"_id": 0, "LocDate": 0, "Hash": 0}
        db = conDB()
        encrypted = db.users.find(inputCommand, filterLoc)
        for x in encrypted:
            tmp = decrypt(x["PhoneNumber"])
            unencrypted.append(tmp)
    unencrypted = list(dict.fromkeys(unencrypted))
    for x in unencrypted:
        covidAlert(x)


class ScheduleThread(threading.Thread):

    def __init__(self, function):
        threading.Thread.__init__(self)
        self.runnable = function
        self.daemon = True

    def run(self):
        self.runnable()

########################################DISTANCE CALCULATION###########################################################
def squareRange(lat, lon):#outputs a set of points that make up a square of side length 50m
    latmin = float(lat) - 0.225
    latmax = float(lat) + 0.225
    lonmin = float(lon) - (25/(111111*math.cos(math.radians(float(lat)))))
    lonmax = float(lon) + (25/(111111 * math.cos(math.radians(float(lat)))))
    range = [latmin, latmax, lonmin, lonmax]
    return range

###########################################ENCRYPTING AND HASHING######################################################
def encrypt(msg):
    msg = str(msg).encode()
    encrypted = f.encrypt(msg)
    return encrypted


def decrypt(encrypted):
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


#############################################SERVER START UP###########################################################
count  = 0
while 1:
    print("Enter password: ")
    password = "12345678" #input()
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
    jsondata = request.json
    data = json.loads(jsondata)
    phone_number = data['phone_number']
    longitude = data['lon']
    latitude = data['lat']
    #commented out for not having db setup
    #pingDB(phone_number, longitude, latitude)

    #for debugging
    print(str(phone_number) + "\n" + str(latitude) + "\n" + str(longitude))

    return jsonify(response_value_1=1, response_value_2=True)


@app.route('/auth_request_code', methods=['POST'])
def auth_request_code():
    jsondata = request.json
    data = json.loads(jsondata)
    phone_number = data['phone_number']
    signature = data['signature']
    auth_code = sendSMSCode(phone_number)
    codeWrite(phone_number, signature, auth_code)
    sent_msg = {'msg': "Text message has been sent"}
    # TODO: Send text message
    return json.dumps(sent_msg)


@app.route('/auth_check_code', methods=['POST'])
def auth_check_code():
    jsondata = request.json
    data = json.loads(jsondata)
    phone_number = data['phone_number']
    signature = data['signature']
    received_code = data['code']
    resp = codeRead()
    code = resp['fCode']
    sig = resp['signature']
    # TODO: add more checks (similar to the mock server)
    if(str(received_code) == str(code) and str(signature) == str(sig)):
        print("codes match")
        #commented out for not having db setup
        #register(phone_number)
        return flask.Response(status=204)
    else:
        return flask.Response(status=401)

@app.route('/nurse_logon', methods=['POST'])
def nurse_logon():
    jsondata = request.json
    data = json.loads(jsondata)
    password = data['password']
    print(password)
    # this is simply the hash_string of 87654321, the current nurse password
    if(hash_string(password) == \
            'e24df920078c3dd4e7e8d2442f00e5c9ab2a231bb3918d65cc50906e49ecaef4'):
        print("nurse logon successful")
        return flask.Response(status=204)
    else:
        print("nurse logon failed")
        return flask.Response(status=401)



@app.route('/nurse_add_data', methods=['POST'])
def nurse_add_data():
    jsondata = request.json
    data = json.loads(jsondata)
    phone_number = data['phone_number']
    #commented out for not having db setup
    #covidLOC(phone_number)
    return flask.Response(status=204)

thread = ScheduleThread(declutterDB)
thread.start()
app.run(host="0.0.0.0",port=os.environ["PORT"],debug=True)
