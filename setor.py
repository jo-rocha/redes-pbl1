from asyncio.windows_events import NULL
from crypt import methods
import json
from operator import methodcaller, truediv
from urllib import response
import paho.mqtt.client as mqtt
import time
from uuid import getnode as get_mac
import threading
from flask import Flask
from flask import request
import json
import threading
import random
import requests
clientID = 'sector'

list_tcans = []
ordem = None
sectorID = None
coordinator = None
sectorPriority = None
electionCounter = 0
sectorList = None

# Configurações do client mqtt
broker = 'mqtt.eclipseprojects.io'
port_mqtt = 1883
topic_sector = None
client = mqtt.Client()

##################################### API #####################################
FLASK_ENV = "development"
FLASK_APP = "setor"
port_api = 8080
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASK_ENV', silent=True)
app.config.from_envvar('FLASK_APP', silent=True)


# Função para retormar as x lixeiras mais criticas
@app.route('/list-tcans')
def list_tcan():
    args = request.args
    number_tcans = int(args.get('number'))
    sector = int(args.get('sector'))#VAI PRECISAR MESMO DESSA INFORMAÇÃO?
    status = False
    list_tcans_temp = []
    for x in range(number_tcans):
        list_tcans_temp.append(list_tcans[x])
        status = False
    
    value = {
        "status": status,
        "data": list_tcans_temp,
        "message": "Lixeiras resgatadas com sucesso" if status else "Erro ao resgatar lixeiras"
    }

    return "a"

# Função para esvaziar lixeira
@app.route('/dump-tcan')
def dump_tcan():
    args = request.args
    sector = int(args.get('sector'))
    id_tcan = int(args.get('sector'))
    status = False
    #É possivel solicitar para descartar o lixo da lixeira a partir de outro setor sem ser o qual o caminhão pertence?
    if sectorID == sector:
        # Realizar procedimento de descarte do lixo
        pass
    else:
        # Procurar qual a porta da api do setor especificado na rota
        pass
    for tcan in list_tcans:
        if tcan['id'] == id_tcan:
            tcan['currentLoad'] = 0
            value = {
                "setor": sector,
                "id": str(id_tcan),
                "value": 0,
            }
            topic_lixeira = f'sector/sector{sector}/lixeira{id_tcan}'
            send_message('update_data',value,topic_lixeira)
            status = True
    response = {
        "status": status,
        "message": "Lixeira esvaziada com sucesso" if status else "Erro ao esvaziar lixeira"
    }
    return json.dumps(response)

#Funcao para reservar as lixeiras
@app.route('/reserve-tcan')
def reserve_tcan():
    global electionCounter
    global sectorList
    # reserveTcanList = request.json() precisa testar se isso só já da o loads ou se por set um get eu tenho que pegar o payload antes
    reserveTcanList = requests.args.get('reserve')
    if sectorID == coordinator and electionCounter < 2:
        electionCounter+= 1
        pass#vai procurar a se tem alguma lixeira que está nesse setor, e se não enviar os requests para os outros setores
    elif electionCounter >= 2:
        callElection()
    else:
        #se ele não for o coordenador ele vai passar o request para quem está sendo o coordenador no momento
        for i in sectorList:
            if i['secID'] == coordinator:
                coordPort = i['secPort']
        response = requests.get(f'http://127.0.0.1:{coordPort}/reserve-tacn?tcanRequest={reserveTcanList}')
        #falta ainda lidar com o response

#Bloco responsavel por atualizar o número de prioridade deste setor quando o entao coordenador chamar uma nova eleicao
@app.route('/election')
def update_priority():
    global sectorPriority
    sectorPriority = random.randint(0,100)
    return sectorPriority

@app.route('/update-sector-list', methods=['POST'])
def update_sector_list():
    global sectorList
    sectorList = requests.json()#TALVEZ PRECISE MUDAR CASO O JSON NÃO DE O LOADS JÁ
    return None
    
def start_api():
    global port_api
    app.run(port=port_api)

##################################### BLOCO MQTT #####################################

# Bloco responsável pelo processo de subscribe em um tópico.
def on_connect(client, userdata, flags, rc):  
    global topic_sector
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)
    
    # O subscribe fica no on_connect pois, caso perca a conexão ele a renova
    # Lembrando que quando usado o #, você está falando que tudo que chegar após a barra do topico, será recebido
    client.subscribe('connection/teste')
    client.subscribe(topic_sector)

# Bloco responável por fazer uma ação quando receber uma mensagem
def on_message(client, userdata, msg):
    print('Entrou')
    
    global sectorID
    msg_temp = str(msg.payload)

    data_message = json.loads(msg.payload.decode())
    
    if sectorID == data_message['value']['setor']:
        if data_message['header'] == 'connection':
                global list_tcans
                id_tcan = len(list_tcans) + 1
                
                tcan = {}
                tcan['id'] = id_tcan
                tcan['setor'] = data_message['value']['setor']
                tcan['currentLoad'] = data_message['value']['currentLoad']

                list_tcans.append(tcan)
                value = {
                    "setor": data_message['value']['setor'],
                    "id": str(id_tcan),
                    "value": data_message['value']['currentLoad'],
                    "lock": data_message['value']['lock']
                }
                arquivo = open(f'setor{sectorID}.txt', 'a')
                arquivo.write(json.dumps(value) + '\n')
                arquivo.close
                send_message('return_id_tcan',value,f'sector/sector{sectorID}/lixeira{str(id_tcan)}')
                send_message('cadastro', value, f'truck')

        elif data_message['header'] == 'update_data':
            for tcan in list_tcans:
                if tcan['id'] == data_message['value']['id']:
                    tcan['currentLoad'] = data_message['value']['currentLoad']
                    tcan['lock'] = data_message['value']['lock']

    print(msg.topic+" -  "+str(msg.payload))

def publish(client,msg,topic_name):
    
    time.sleep(1)
    result = client.publish(topic_name, msg,True)
    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to topic `{topic_name}`")
    else:
        print(f"Failed to send message to topic {topic_name}")
        print(result)

def send_message(route,value,topic):
    
    message = {
        "header":route,
        "value": value,
    }
    
    message = json.dumps(message)
    publish(client,message,topic)

# Bloco responsável por iniciar o client mqtt
def startConection():
    
    global topic_sector
    global sectorID

    request = input('What is the number sector?')
    topic_sector = f'sector/sector{request}'
    sectorID = request

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port_mqtt,60)
    
    receive_thread = threading.Thread(target = start_api)
    receive_thread.start()

    while True:
        # client.subscribe('connection/teste')
        client.loop_start()


if __name__ == '__main__':
    startConection()

##################################### ELEICAO #####################################

def on_execution():
    #quando o setor executa, ele vai enviar uma mensagem avisando a interface que ele está vivo, e vai sortear o seu numero de prioridade
    #a interface vai entao retornar ao setor a lista de outros setores que estao vivos, se e que tem algum
    global sectorPriority
    global sectorID
    global coordinator
    global sectorList
    sectorPriority = random.randint(0,100)
    sectorList = requests.get(f'http://127.0.0.1:5000/inform-get-sectors?secId={sectorID}&secPri={sectorPriority}&secPort={port_api}')#TEM QUE MUDR A PORTA
    sectorList = sectorList.json()#TALVEZ TENHA QUE MUDAR ISSO, EU AINDA NAO TENHO CERTEZA SE ISSO JA DA O LOADS OU NAO
    coordinator = sectorList[0]['sectorID']

def callElection():
    global sectorPriority
    global coordinator
    global sectorList

    sectorPriority = random.randint(0,100)
    for i in sectorList:
        port = i['port_api']
        #o setor que receber a mensagem vai resortear seu valor de prioridade e retornar no request
        i['sectorPriority'] = requests.get(f'http://127.0.0.1:{port}/election')
    #depois disso ele vai ordenar a nova lista de prioridade, atualizar o coordenador e enviar a nova lista para todos os outros setores
    sectorList.sort(key = lambda x: int(x['sectorPriority']))
    coordinator = sectorList[0]['sectorID']
    dumpedSectorList = json.dumps(sectorList)
    for i in sectorList:
        port = i['port_api']
        response = request.post(f'http://127.0.0.1:{port}/update-sector-list', dumpedSectorList)
        
