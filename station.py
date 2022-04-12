import socket
import threading
import constant
import json

clientID = 'tcan'

loadCapacity = 400
currentLoad = 0

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((constant.Host, constant.Port))

def receive():
    global currentLoad
    try:
        while True:

            if currentLoad >= loadCapacity:
                currentLoad = 0
                print('[DEPOSIT STATION HAS BEEN CLEANED]\n')
                print(f'[THE DEPOSIT STATION CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n')

            message = client.recv(1024).decode('ascii')
            messageRoute = decode_message_route(message)
            # se a estação receber uma mensagem do caminhão avisando que ele desepejou lixo na estação
            if messageRoute['route'] == 'dump':
                currentLoad += messageRoute['trashLoad']
                print(f'[THE DEPOSIT STATION CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n')
            else:
                print('wrong message on station')

    except:
        print('[STATION ERROR]')

def decode_message_route(message):
    result = json.loads(message)

    return result

receive_thread = threading.Thread(target = receive)
receive_thread.start()