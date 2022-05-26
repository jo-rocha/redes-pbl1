from asyncio.windows_events import NULL
import json
from operator import truediv
import paho.mqtt.client as mqtt
import random
import time
from uuid import getnode as get_mac

# from getmac import get_mac_address as gma
clientID = 'tcan'

# Trashcan attributes
loadCapacity = None
currentLoad = random.randint(0, 1000)
lock = None
ordem = None

# Configurações do client mqtt
broker = 'mqtt.eclipseprojects.io'
port = 1883
topic = "conexao"
client = mqtt.Client()

# Bloco responsável pelo processo de subscribe em um tópico.
def on_connect(client, userdata, flags, rc):  
    
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)
    
    # O subscribe fica no on_connect pois, caso perca a conexão ele a renova
    # Lembrando que quando usado o #, você está falando que tudo que chegar após a barra do topico, será recebido
    client.subscribe("setor/estacao1/#")

# Bloco responável por fazer uma ação quando receber uma mensagem
def on_message(client, userdata, msg):
    print(msg.topic+" -  "+str(msg.payload))


def publish(client,msg,topic_name):
    msg_count = 0
    while True:
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
        msg_count += 1

# Bloco responsável por iniciar o client mqtt
def startConection():
    global controle_conexao
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()


    mac = ':'.join(("%012X" % get_mac())[i:i+2] for i in range(0, 12, 2))
    if(controle_conexao == '0'):
        print('ia')
        controle_conexao = '1'
        client.loop_stop()
        publish(client,"{'ID':'tcan','MAC':'" + mac + "'}",topic)
    
    

# Connecting to Server
# client = startConection()


if __name__ == '__main__':
    startConection()
