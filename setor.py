from asyncio.windows_events import NULL
import json
from operator import truediv
import paho.mqtt.client as mqtt
import random
import time
from uuid import getnode as get_mac
import threading

clientID = 'sector'

list_tcans = []
ordem = None
id_sector = None

# Configurações do client mqtt
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
def on_message(client, userdata, msg):
    print('Entrou')
    
    global id_sector
    msg_temp = str(msg.payload)

    data_message = json.loads(msg.payload.decode())
    
    if id_sector == data_message['value']['setor']:
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
                arquivo = open(f'setor{id_sector}.txt', 'a')
                arquivo.write(json.dumps(value) + '\n')
                arquivo.close
                send_message('return_id_tcan',value,f'sector/sector{id_sector}')
                send_message('cadastro', value, f'truck')#manda para o caminhão adicionar a lixeira nova

        elif data_message['header'] == 'update_data':
            for tcan in list_tcans:
                if tcan['id'] == data_message['value']['id']:
                    tcan['currentLoad'] = data_message['value']['currentLoad']
                    tcan['lock'] = data_message['value']['lock']
                    tcans.append(json.dumps(tcan) + '\n')

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
    global id_sector

    request = input('What is the number sector?')
    topic_sector = f'sector/sector{request}'
    id_sector = request

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


if __name__ == '__main__':
    startConection()
