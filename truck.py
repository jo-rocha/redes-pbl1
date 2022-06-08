from ast import IsNot
from ctypes.wintypes import tagRECT
import paho.mqtt.client as mqtt
import json
import time
import os
import threading

# from pbl1.truck import organize_tcan_list

currentLoad = 0
loadCapacity = 150
tcanList = []

clientID = 'truck'

##MQTT START##
broker = 'mqtt.eclipseprojects.io'
port = 1883
client = mqtt.Client()

# Bloco responsável por iniciar o client mqtt
def startConection():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    client.loop_start()

# Bloco responsável pelo processo de subscribe em um tópico.
def on_connect(client, userdata, flags, rc):  
    
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)
    
    # O subscribe fica no on_connect pois, caso perca a conexão ele a renova
    # Lembrando que quando usado o #, você está falando que tudo que chegar após a barra do topico, será recebido
    client.subscribe("truck")

    #publish_thread = threading.Thread

# Bloco responável por fazer uma ação quando receber uma mensagem
def on_message(client, userdata, msg):
    # global tcanList
    # global currentLoad
    # global loadCapacity
    #O caminhao recebe mensgens quando uma lixeira é atualizada, então toda vez ele vai atualizar a lista de lixeiras
    organize_tcan_list(msg.payload)


def publish(client,msg,topic_name):
    msg_count = 0
    while True:
        time.sleep(1)
        # msg = f"messages: {msg_count}"
        result = client.publish(topic_name, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Sent `{msg}` to topic `{topic_name}`")
        else:
            print(f"Failed to send message to topic {topic_name}")
            print(result)
        msg_count += 1

        # message = {
        # "header": header, - cadastro, status,
        # "value": value, - quantidade de lixo atual,
        # "id": id,
        # "setor": setorx,
        # "message": message,
        # }    
def organize_tcan_list(msg):
    global tcanList
    msg = json.loads(msg.decode())
    if msg['header'] == 'cadastro':#cria um dicionário com as informações de cada lixeira
        tcan = {}
        tcan['id'] = msg['value']['id']
        tcan['setor'] = msg['value']['setor']
        tcan['currentLoad'] = msg['value']['value']
        tcanList.append(tcan)
    elif msg['header'] == 'status':#a lixeira recebeu lixo e mandou seu status para o caminhão. O caminhão atualiza a lixeira e faz o resorting da lista
        for i in tcanList:
            if i['id'] == msg['value']['id']:
                i['currentLoad'] = msg['value']['value']#atualiza o valor da lixeira na lista do caminhão
                tcanList.sort(key = lambda x: int(x['currentLoad']), reverse = True)
            
#vai pegar a lixeira do topo da lista de prioridade e fazer o processo de ir até a lixeira e a esvaziar        
def find_execute_route():
    global tcanList
    global currentLoad
    global loadCapacity
    startConection()
    while True:
        if tcanList:#se a lista nao estiver vazia
            #[interface beginning]
            time.sleep(5)
            os.system('cls||clear')
            goalTcan = tcanList[0]
            if goalTcan['currentLoad'] == 0:
                print(f'[THERE ARE NO MORE TRASHCANS TO COLLECT, AND THE TRUCK LOAD IS {currentLoad}/{loadCapacity}]')
            else:
                print(f'[THE TRUCK CURRENT LOAD IS {currentLoad}/{loadCapacity}, AND IT IS HEADING TOWARDS THE TRASHCAN:{tcanList[0]}]\n')
            #[interface end]
            # goalTcan = tcanList.pop(0)
            aux = int(goalTcan['currentLoad']) + currentLoad
            if aux >= loadCapacity:
                print('[THE TRUCK CAN\'T HOLD THIS AMOUNT OF TRASH]\n[UNLOADING AT THE STATION...]')
                currentLoad = 0 
                time.sleep(5)
            else:
                tcanList.pop(0)#já que eu já pego o topo na linha 100
                time.sleep(5)
                client.publish(goalTcan['setor'], goalTcan['id'])#quando o caminhão chega na lixeira ele publica no tópico da lixeira e o payload é o id da lixeira a ser esvaziada
                #quando ele esvazia a lixeira ele a coloca de volta no final da lista de lixeiras
                currentLoad += int(goalTcan['currentLoad'])
                goalTcan['currentLoad'] = 0
                tcanList.append(goalTcan)
        else:
            time.sleep(5)
            os.system('cls||clear')
            print(f'[NO TRASHCANS REGISTERED IN THE SYSTEM YET]')


message = input('[PRESS ANY KEY TO START THE TRUCK]')
find_execute_route()
# find_execute_route_thread = threading.Thread(target = find_execute_route)
# find_execute_route_thread.start()
