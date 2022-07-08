from wsgiref.validate import InputWrapper
import paho.mqtt.client as mqtt
import json
import time
import os
import threading
import requests
from flask import Flask
from flask import request

truckList = []
sectorList = []
##################################### API #####################################
FLASK_ENV = "development"
FLASK_APP = "interface"
port_api = 8088
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASK_ENV', silent=True)
app.config.from_envvar('FLASK_APP', silent=True)

@app.route('/inform-get-sectors')
def addSector():
    global sectorList
    newSector = {}
    newSector['sectorID'] = requests.args.get('sectorID')
    newSector['sectorPriority'] = requests.args.get('sectorPriority')
    newSector['port_api'] = requests.args.get('port_api')
    sectorList.append(newSector)
    sectorList.sort(key = lambda x: int(x['sectorPriority']))
    dumpedSectorList = json.dumps(sectorList)
    #ordena a lista e manda para todos os servidores atualizarem
    for i in sectorList:
        if i['sectorID'] != newSector['sectorID']:
            port = i['api_port']
            response = requests.post(f'http://127.0.0.1:{port}/update-sector-list', {dumpedSectorList})
    return dumpedSectorList

##################################### INTERFACE #####################################
def runInterface():
    while True:
        if not truckList:
            print("[THERE ARE NO TRUCK REGISTERED IN THE SYSTEM YET]")
        else:
            while True:
                os.system('cls||clear')
                print("#################################################")
                for i in truckList:
                    print(f"{i}\n")
                print("#################################################")
                userInput = input("[SELECT A TRUCK ID TO GIVE FURTHER INSTRUCTIONS OR PRESS 'S' TO SEND THE REQUEST]\n")
                if userInput == 's':
                    pass#manda o request para setor
                    break
                else:
                    for i in truckList:
                        if i['id'] == userInput:
                            print(f"{i}\n")
                            requestNumber = input("[HOW MANY TRASHCANS DO YOU WANT TO SEE?]\n")
                            i['requestNumber'] = requestNumber
                            break
            while True:
                os.system('cls||clear')
                print("#################################################")
                for i in truckList:
                    print(f"{i}\n")
                print("#################################################")
                userInput = input("[SELECT A TRUCK ID TO GIVE FURTHER INSTRUCTIONS OR PRESS 'S' TO SEND THE RESERVEATION REQUEST]\n")
                if userInput == 's':
                    pass#manda o request para o setor
                    break
                else:
                    for i in truckList:
                        if i['id'] == userInput:
                            requestList = i['requestList']
                            print("[THESE ARE THE TRASHCANS REQUESTED BY THE TRUCK]\n")
                            for j in requestList:
                                print(f"{j}\n")
                                
                            reserveList = []
                            userInput = input("[SELECT WHICH TRASHCANS YOU WANT TO RESERVE BY THEIR IDs, SEPARATING THEM BY ',']\n")
                            for k in userInput:
                                if k == ',':
                                    pass
                                else:
                                    reserveList.append(i)
                            i['reserveList'] = reserveList

runInterface()
                        