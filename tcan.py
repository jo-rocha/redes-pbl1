from asyncio.windows_events import NULL
import json
import paho.mqtt.client as mqtt
import random
import time

clientID = 'tcan'

# Trashcan attributes
loadCapacity = None
currentLoad = None
lock = None
ordem = None

# Configurações do client mqtt
broker = 'mqtt.eclipseprojects.io'
port = 1883
topic = "setor/estacao/lixeira"
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


def publish(client,msg):
    msg_count = 0
    while True:
        time.sleep(1)
        # msg = f"messages: {msg_count}"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
            print(result)
        msg_count += 1

# Bloco responsável por iniciar o client mqtt
def startConection():
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    publish(client,"é um teste")

# Connecting to Server
# client = startConection()


if __name__ == '__main__':
    startConection()
