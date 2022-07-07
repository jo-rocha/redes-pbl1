from asyncio.windows_events import NULL
import json
from operator import truediv
import paho.mqtt.client as mqtt
import random
import time
from uuid import getnode as get_mac
import threading
import requests

clientID = 'sector'

list_tcans = []
ordem = None
sectorID = None
sectorPriority = None
coordinator = None

#configuracao mqtt
broker = 'mqtt.eclipseprojects.io'
port = 1883
topic_sector = None
client = mqtt.Client()


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
def on_message(client, userdata, msg):# VAI TER QUE MUDAR A LOGICA DE MANDAR AS LIXEIRAS PARA O CAMINHAO
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
                send_message('return_id_tcan',value,f'sector/sector{sectorID}')
                send_message('cadastro', value, f'truck')#manda para o caminhão adicionar a lixeira nova

        elif data_message['header'] == 'update_data':
            for tcan in list_tcans:
                if tcan['id'] == data_message['value']['id']:
                    tcan['currentLoad'] = data_message['value']['currentLoad']
                    tcan['lock'] = data_message['value']['lock']
                    tcans.append(json.dumps(tcan) + '\n')

    print(msg.topic+" -  "+str(msg.payload))


#metodo do mqtt
def publish(client,msg,topic_name):
    
    time.sleep(1)
    result = client.publish(topic_name, msg,True)
    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to topic `{topic_name}`")
    else:
        print(f"Failed to send message to topic {topic_name}")
        print(result)

#bloco responsavel por formatar a mesnagem que ai ser enviada pelo metodo publish
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

    request = input('What is the number of the sector?')
    topic_sector = f'sector/sector{request}'
    sectorID = request

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port,60)
    
    while True:
        # client.subscribe('connection/teste')
        client.loop_start()

    # receive_thread = threading.Thread(target = on_message)
    # receive_thread.start()
    

# Connecting to Server
# client = startConection()

#bloco responsavel por iniciar a comunicação par avisar a interface da existencia do setor, e iniciar uma eleicao
def onExecution():
    global sectorPriority
    global sectorID
    global coordinator
    sectorPriority = random.randint(0,100)
    #quando o setor executa, ele vai enviar uma mensagem avisando a interface que ele está vivo, e vai sortear o seu numero de prioridade
    #a interface vai entao retornar ao setor a lista de outros setores que estao vivos, se e que tem algum
    sectorDict = requests.get(f'http://127.0.0.1:5000/inform-get-sectors?secId={sectorID}&secPri={sectorPriority}')#TEM QUE MUDR A PORTA
    sectorDict = sectorDict.json()#TALVEZ TENHA QUE MUDAR ISSO, EU AINDA NAO TENHO CERTEZA SE ISSO JA DA O LOADS OU NAO
    coordinator = sectorDict[0]['sectorID']

if __name__ == '__main__':
    startConection()
