from asyncio.windows_events import NULL
from cgitb import reset
import json
from operator import truediv
import paho.mqtt.client as mqtt
import random
import time
from uuid import getnode as get_mac
import threading

# from getmac import get_mac_address as gma
clientID = 'tcan'

# Trashcan attributes
loadCapacity = None
currentLoad = random.randint(0, 1000)
lock = '1'
ordem = None
id = None
# Configurações do client mqtt
broker = 'mqtt.eclipseprojects.io'
port = 1883
topic = "connection"
topic_sector = None
topic_lixeira = ''
client = mqtt.Client()


# Bloco responsável pelo processo de subscribe em um tópico.
def on_connect(client, userdata, flags, rc):  
    
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)
    
    # O subscribe fica no on_connect pois, caso perca a conexão ele a renova
    # Lembrando que quando usado o #, você está falando que tudo que chegar após a barra do topico, será recebido
    # client.subscribe(topic_lixeira)

# Bloco responável por fazer uma ação quando receber uma mensagem
def on_message(client, userdata, msg):
    global currentLoad
    global lock
    global id
    
    data_message = json.loads(msg.payload.decode())
    if data_message['header'] == 'return_id_tcan':
        if id == None:
            id = data_message['value']['id']
    
    elif data_message['header'] == 'update_data':
        if data_message['value']['id'] == id:
            currentLoad = data_message['value']['currentLoad']
            lock = data_message['value']['lock']
    
    print(msg.topic+" -  "+str(msg.payload))


def publish(client,msg,topic_name):
    time.sleep(1)
    # msg = f"messages: {msg_count}"
    result = client.publish(topic_name, msg,True)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to topic `{topic_name}`")
    else:
        print(f"Failed to send message to topic {topic_name}")
        print(result)

def send_message(route,value,topic):
    message = ""
    message = {
        "header":route,
        "value": value,
    }
    
    message_temp = json.dumps(message)
    
    publish(client,message_temp,topic)

def generate_trash():
    global currentLoad

    trash = random.randint(0, 100)
    currentLoad = currentLoad + trash

# Bloco responsável por iniciar o client mqtt
def startConection():
    global topic_sector
    global currentLoad
    global lock

    request = input('What is the trash sector?')
    topic_sector = f'sector/sector{request}'
    topic_lixeira = f'sector/sector{request}/lixeira'
    
    
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    value = {
        "setor":str(request),
        "currentLoad":str(currentLoad),
        "lock":lock
    }
    client.subscribe(topic_sector)
    send_message("connection",value,"connection/teste")
    while True:
        client.loop_start()

    # receive_thread = threading.Thread(target = on_message)
    # receive_thread.start()
    

    

# Connecting to Server
# client = startConection()


if __name__ == '__main__':
    startConection()
