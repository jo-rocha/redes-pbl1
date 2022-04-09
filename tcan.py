import socket
import threading
import constant
import json

clientID = 'tcan'

# Trashcan attributes
loadCapacity = 60
currentLoad = 0

# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((constant.Host, constant.Port))

def receive():
    global currentLoad
    try:
        while True:
            message = client.recv(1024).decode('ascii')
            messageRoute = decode_message_route(message)
            
            if messageRoute == 'ID':
                sendMessage = encode_message_send("ID",clientID,clientID,"",0)
                client.send(sendMessage.encode('ascii'))
            
            elif messageRoute == 'dump':
                currentLoad = 0
                sendMessage = encode_message_send("TRASHCAN STATUS",sendMessage,currentLoad,"",0)
                client.send(sendMessage.encode('ascii'))
                
                print(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n')
            
            elif messageRoute == 'status':
                sendMessage = encode_message_send("status",sendMessage,currentLoad,"",0)
                client.send(sendMessage.encode('ascii'))
            
            elif messageRoute == 'set-block':
                status = 1
                sendMessage = encode_message_send("status-released",sendMessage,currentLoad,"",0)
                client.send(sendMessage.encode('ascii'))
                
                print(f'\n\n[THE TRASHCAN IS {"RELEASED" if status == 1 else "BLOCKED"}]\n')
            
            elif messageRoute == 'hello':
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
            trashInput = input(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n\n')
            if trashInput != 'dump':
                if currentLoad < loadCapacity:
                    aux = int(trashInput) + currentLoad
                    if aux > loadCapacity:
                        input('[THE TRASHCAN CANNOT HOLD THIS AMOUNT OF TRASH. INPUT: "ok" TO RETURN]\n\n')
                    else: 
                        currentLoad = aux
                        sendMessage = encode_message_send("status","status",currentLoad,"POST",1)
                        client.send(sendMessage.encode('ascii'))
                else:
                    print("""######################################################################\n#[THE TRASHCAN IS FULL, YOU MUST WAIT FOR THE TRASHCAN TO BE EMPTIED]#\n######################################################################
                    """)
            else:
                toTruck = currentLoad # Guarda uma auxiliar 'toTruck' para quando a lixeira esvaziar mandar a carga para o caminhão
                currentLoad = 0
                sendMessage = encode_message_send("dumped","dumped",currentLoad,"POST",1)
                client.send(sendMessage.encode('ascii'))
                # Mandar a capacidade da lixeira antes de exvaziar
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
