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
    client.subscribe('connection')
    client.subscribe(topic_sector)

# Bloco responável por fazer uma ação quando receber uma mensagem
def on_message(client, userdata, msg):
    global id_sector

    data_message = json.loads(msg)
    if id_sector == data_message['value']['setor']:
        if data_message['header'] == 'connection':
            # Adicionar lixeira na lista de lixeira e mandar o id dela de volta para a lixeira
                global list_tcans
                id_tcan = len(list_tcans) + 1
                
                tcan = {}
                tcan['id'] = id_tcan
                tcan['setor'] = data_message['value']['setor']
                tcan['currentLoad'] = data_message['value']['currentLoad']

                list_tcans.append(tcan)
                value = {
                    'id': id_tcan
                }
                send_message('return_id_tcan',value,f'sector/sector{id_sector}/lixeira')

        elif data_message['header'] == 'update_data':
            # Atualizar dados da lixeira indicada no topic. Salvar os dados em um arquivo ou mandar essa informação via API
            for tcan in list_tcans:
                if tcan['id'] == data_message['value']['id']:
                    tcan['currentLoad'] = data_message['value']['currentLoad']
                    tcan['lock'] = data_message['value']['lock']
            pass
    
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

    publish(client,message,topic)

# Bloco responsável por iniciar o client mqtt
def startConection():
    
    global topic_sector
    global id_sector

    request = input('What is the number sector?')
    topic_sector = f'sector/sector{request}'
    id_sector = request;

    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()

    receive_thread = threading.Thread(target = on_message)
    receive_thread.start()
    

# Connecting to Server
# client = startConection()


if __name__ == '__main__':
    startConection()
