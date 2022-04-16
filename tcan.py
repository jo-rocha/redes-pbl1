import socket
import threading
import constant
import json

clientID = 'tcan'

# Trashcan attributes
loadCapacity = 60
currentLoad = 0
lock = "0"
ordem = -1
# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((constant.Host, constant.Port))

def receive():
    global currentLoad
    global lock
    global ordem
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
                if int(ordem) < 0:
                    ordem = -2
                print(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n')
            
            elif messageRoute == 'status':
                sendMessage = encode_message_send("status",currentLoad,currentLoad,"",0)
                client.send(sendMessage.encode('ascii'))
            
            elif messageRoute == 'set-block':
                # if lock == "1":
                #     lock = "0" 
                # else:
                #     lock = "1"
                # new_value =  abs(int(lock) - 1);
                # lock = str(new_value)
                print(f'Valor atual: {currentLoad}')
                lock = "0" if lock == "1" else "1"
                sendMessage = encode_message_send("released",lock,lock,"",0)
                print(sendMessage)
                client.send(sendMessage.encode('ascii'))
                
                print(f'"[THE TRASHCAN IS {"BLOCKED" if lock == "1" else "RELEASED"}]"\n')
            elif messageRoute == 'set-list-tcans':
                 messageResponse = json.loads(message)["value"]

                 print(messageResponse)
                 print("[TRASH CANS LIST UPDATED]")
            elif messageRoute == 'hello':
                print(message)
    except:
        print('[ERROR TRASHCAN]')
        client.close()
        return None

def write():
    global currentLoad
    global ordem
    try:
        while True:
            # trashInput = input('[IF YOU WANT TO THROW TRASH IN THE TRASHCAN INPUT THE AMOUNT OF TRASH:]\n')
            # currentLoad = currentLoad + int(trashInput)
            # print(currentLoad)
            # ##added
            # client.send('message from the tcan'.encode('ascii'))
            trashInput = input(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{loadCapacity} AND THE TRASHCAN IS {"BLOCKED" if lock == "1" else "RELEASED"} ]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n\n')
            if trashInput != 'dump':
                if currentLoad < loadCapacity:
                    aux = int(trashInput) + currentLoad
                    if aux > loadCapacity:
                        input('[THE TRASHCAN CANNOT HOLD THIS AMOUNT OF TRASH. INPUT: "ok" TO RETURN]\n\n')
                    elif lock == '1':
                        print(currentLoad)
                        input('[THE TRASHCAN IS BLOCKED. INPUT: "ok" TO RETURN]\n\n')
                    else: 
                        currentLoad = aux
                        sendMessage = encode_message_send("status","status",currentLoad,"POST",0)
                        client.send(sendMessage.encode('ascii'))
                        if int(ordem) < 0:
                            ordem = -1
                else:
                    print("""######################################################################\n#[THE TRASHCAN IS FULL, YOU MUST WAIT FOR THE TRASHCAN TO BE EMPTIED!]#\n######################################################################
                    """)
            else:
                toTruck = currentLoad # Guarda uma auxiliar 'toTruck' para quando a lixeira esvaziar mandar a carga para o caminhão
                currentLoad = 0
                sendMessage = encode_message_send("dumped","dumped",currentLoad,"POST",0, toTruck)
                if int(ordem) < 0:
                    ordem = -2
                client.send(sendMessage.encode('ascii'))
                # Mandar a capacidade da lixeira antes de exvaziar
    except:
        client.close()
        return None
        
def decode_message_route(message):
    result = json.loads(message)

    return result["header"]["route"]

def encode_message_send(route,message,value,method,type, value2 = None):
    # se type igual a 0 é um send que responde uma requisição e de for 1 é um send que envia um requisição
    message = ""
    if type == 0:
        message = {
            "header":{
                "typeResponse": route,
            },
            "value": value,
            "message": message,
            "value2": value2
        }
    else:
        message = {
            "header":{
                "method": method,
                "route": route,
            },
            "value": value,
            "message": message,
            "value2": value2
        }

    return json.dumps(message)     
    
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()
