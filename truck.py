import paho.mqtt.client as mqtt
import json
import time

from pbl1.truck import organize_tcan_list

currentLoad = 0
loadCapacity = 500
tcanList = None

clientID = 'truck'

##MQTT START##
broker = 'localhost'
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
    client.subscribe("caminhao")

    #publish_thread = threading.Thread

# Bloco responável por fazer uma ação quando receber uma mensagem
def on_message(client, userdata, msg):
    #print(msg.topic+" -  "+str(msg.payload))
    global tcanList
    global currentLoad
    global loadCapacity
    # msg = json.loads(msg.payload.decode())
    # if msg['header'] == 'cadastro':
    #     organize_tcan_list()
    # elif msg['header'] == 'status':
    #     pass
    organize_tcan_list(msg)


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
    
def organize_tcan_list(msg):
    if msg['header']
        # message = {
        # "header": header, - cadastro, status
        # "value": value, - quantidade de lixo atual
        # "message": message,
        # "message2":
        # "value2": value2 - quantidade de lixo jogado fora
        # } 
