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
truckIDCounter = 0
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
    global truckIDCounter
    global truckList
    newSector = {}
    newSector['sectorID'] = requests.args.get('sectorID')
    newSector['sectorPriority'] = requests.args.get('sectorPriority')
    newSector['port_api'] = requests.args.get('port_api')
    sectorList.append(newSector)
    sectorList.sort(key = lambda x: int(x['sectorPriority']))
    dumpedSectorList = json.dumps(sectorList)
    ##criando novo caminhao start##
    truck = {}
    truckIDCounter+=1
    truck['ID'] = truckIDCounter
    truck['sector'] = newSector['sectorID']
    truckList.append(truck)
    #o caminhao vai ter mais os campos de numero de lixeiras requisitadas, lixeiras reservadas e numero de lixeiras requisitadas
    ##criando novo caminhao end##

    #ordena a lista e manda para todos os servidores atualizarem
    for i in sectorList:
        if i['sectorID'] != newSector['sectorID']:
            port = i['api_port']
            # Quando quiser mandar um json pela rota é preciso adicionar esse headers e mandar o json dessa forma, igualando a data.
            headers = {'content-type': 'application/json'}
            response = requests.post(f'http://127.0.0.1:{port}/update-sector-list',data=json.dumps(dumpedSectorList), headers=headers)
    
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
                    print(f"[TRUCK: {i['ID']}\n")
                print("#################################################")
                userInput = input("[SELECT A TRUCK ID TO GIVE FURTHER INSTRUCTIONS OR PRESS 'S' TO SEND THE REQUEST]\n")
                if userInput == 's':
                    pass#manda o request para setor
                    break
                else:
                    for i in truckList:
                        if i['ID'] == userInput:
                            requestNumber = input("[HOW MANY TRASHCANS DO YOU WANT TO REQUEST?]\n")
                            i['requestNumber'] = requestNumber
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
                        if i['ID'] == userInput:
                            requestList = i['requestList']
                            print("[THESE ARE THE TRASHCANS REQUESTED BY THE TRUCK]\n")
                            for j in requestList:
                                print(f"{j}\n")
                                
                            reserveList = []
                            userInput = input("[SELECT WHICH TRASHCANS YOU WANT TO RESERVE. ENTER THE SECTOR ID FOLLOWED BY ',' THEN THE TRASHCAN ID\nTO SEPARATE ONE REQUEST FROM THE OTHER USE ';']\n")
                            counter = 0
                            dict = {}
                            sectorAlreadyExists = [0, 0]
                            for k in userInput:
                                sectorAlreadyExists[0] = 0
                                if counter == 4: counter = 0                        
                                if k == ',':
                                    pass
                                elif k == ';':
                                    pass
                                elif counter == 0:   
                                    for l in reserveList:
                                        if l['sector'] == k:
                                            sectorAlreadyExists[0] = 1
                                            sectorAlreadyExists[1] = k
                                    if sectorAlreadyExists[0] == 0:
                                        dict['sector'] = k
                                elif counter == 2:
                                    if sectorAlreadyExists[0] == 1:
                                        for m in reserveList:
                                            if m['sector'] == sectorAlreadyExists[1]:
                                                appendList = m['tcan']
                                                appendList.append(k)
                                    else:
                                        list = []
                                        list.append(k)
                                        dict['tcan'] = list
                                counter += 1
                            i['reserveList'] = reserveList

runInterface()
                        