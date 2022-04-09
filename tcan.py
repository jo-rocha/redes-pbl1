from email import message_from_file
import json
import socket
import threading
import constant

clientID = 'tcan'

# Trashcan attributes
loadCapacity = 60
currentLoad = 0
status = 1

# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((constant.Host, constant.Port))

def receive():
    global currentLoad
    try:
        while True:
            message = client.recv(1024).decode('ascii')
            print("Entrou servidor")
            messageRoute = decode_message_route(message)
            if messageRoute == 'ID':
                sendMessage = encode_message_send("ID",clientID,clientID,"",0)
                client.send(sendMessage.encode('ascii'))
                # client.send(clientID.encode('ascii'))
            elif messageRoute == 'dump':
                currentLoad = 0
                # sendMessage = f'<TRASHCAN STATUS: {str(currentLoad)}>'
                sendMessage = encode_message_send("TRASHCAN STATUS",sendMessage,currentLoad,"",0)
                client.send(sendMessage.encode('ascii'))
                print(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n')
            elif messageRoute == 'status':
                print("Entrou rota status")
                sendMessage = f'status:{str(currentLoad)}'
                sendMessage = encode_message_send("status",sendMessage,currentLoad,"",0)
                client.send(sendMessage.encode('ascii'))
            elif messageRoute == 'set-block':
                status = 1
                # sendMessage = f'status-released:{"released" if status == 1 else "blocked"}'
                sendMessage = encode_message_send("status-released",sendMessage,currentLoad,"",0)
                client.send(sendMessage.encode('ascii'))
                print(f'\n\n[THE TRASHCAN IS {"RELEASED" if status == 1 else "BLOCKED"}]\n')
            elif message == 'hello':
                print(message)
    except:
        print('[ERROR TRASHCAN]')
        client.close()
        return None

def write():
    global currentLoad
    try:
        while True:
            # trashInput = input('[IF YOU WANT TO THROW TRASH IN THE TRASHCAN INPUT THE AMOUNT OF TRASH:]\n')
            # currentLoad = currentLoad + int(trashInput)
            # print(currentLoad)
            # ##added
            # client.send('message from the tcan'.encode('ascii'))
            if currentLoad < loadCapacity:
                trashInput = input(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n\n')
                aux = int(trashInput) + currentLoad
                if aux > loadCapacity:
                    input('\n\n[THE TRASHCAN CANNOT HOLD THIS AMOUNT OF TRASH. INPUT: "ok" TO RETURN]\n\n')
                else: 
                    currentLoad = aux
                    sendMessage = encode_message_send("status","status",currentLoad,"POST",1)
                    client.send(sendMessage.encode('ascii'))
                    # client.send(f'status:{str(currentLoad)}'.encode('ascii'))
            else:
                input('\n\n[THE TRASHCAN IS FULL, YOU MUST WAIT FOR THE TRASHCAN TO BE EMPTIED]\n[INPUT: "ok" TO RELOAD THE STATUS OF THE TRASHCAN]\n\n')
    except:
        client.close()
        return None
        
def decode_message_route(message):
    result = json.loads(message)

    return result["header"]["route"]

def encode_message_send(route,message,value,method,type):
    # se type igual a 0 é um send que responde uma requisição e de for 1 é um send que envia um requisição
    message = ""
    if type == 0:
        message = {
            "header":{
                "typeResponse": route,
            },
            "value": value,
            "message": message
        }
    else:
        message = {
            "header":{
                "method": method,
                "route": route,
            },
            "value": value,
            "message": message
        }

    return json.dumps(message)

receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()
