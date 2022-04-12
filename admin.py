from ctypes.wintypes import PINT
import socket
import threading
import constant
import json

clientID = 'admin'
list_tcans = []
#Connection to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((constant.Host, constant.Port))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            messageRoute = decode_message_route(message)
            if messageRoute == 'ID':
                sendMessage = encode_message_send("ID",clientID,clientID,"",0,"")
                client.send(sendMessage.encode('ascii'))
                # client.send(clientID.encode('ascii'))
            # elif messageRoute == 'get-next-tcan':
            #     # Retorna a próxima lixeira da lista de lixeiras
            #     sendMessage = encode_message_send("ID",clientID,clientID,"",0,"")
            #     client.send(sendMessage.encode('ascii'))
            #     pass
            elif messageRoute == 'get-list-tcan':
                # Retorna a lista de lixeiras já ordenadas
                sendMessage = encode_message_send("trashcan-list",sendMessage,"","",0,"")
                client.send(sendMessage.encode('ascii'))
                pass
            elif messageRoute == 'set-list-tcans':
                messageResponse = json.loads(message)["value"]
                messageResponse = update_list_tcans(messageResponse)
                print("[TRASH CANS LIST UPDATED]")
        except:
            print('[ERROR ADMIN!]')
            break


def write():
    controle = 1
    # try:
    while True:
        if controle == 1:
            request = input('[CHOOSE AN OPERATION]\n1-CHANGE STATUS TRASHCAN\n2-CHANGE CAPACITY TRASHCAN\n3-GET STATUS TRASHCANS\n4-CHANGE ORDER LIST TRASHCANS\n5-CLOSE\n\n\n\n\n')
            if request == "1":
                change_status_tcan()
            elif request == "2":
                change_capacity_tcan()
            elif request == "3":
                get_status_tcans()
            elif request == "4":
                change_order_list_tcan()
            elif request == "5":
                controle = 0
            else:
                print("[CHOOSE VALID OPTION]\n\n\n")
        else:
            print("CLOSING APPLICATION...")
            client.close()
            break
    # except:
    #     client.close()
    #     return None
        # client.send(message_JSON.encode('ascii'))

# Change status the tcan (blocked or released)
def change_status_tcan():
    message = "set-block"
    tcan_id = input('[CHOOSE THE TRASCAN]\n')
    message = encode_message_send("set-block",tcan_id,tcan_id,"PUT",1,"tcan")
    client.send(message.encode('ascii'))

# Change the capacity tcan
def change_capacity_tcan():
    message = encode_message_send("get-tcans","","","GET",1,"tcan")
    client.send(message.encode('ascii'))
    
    message = client.recv(1024).decode('ascii')
    response = json.loads(message)
    request = input('[CHOOSE THE TRASCAN]\n')
    id_tcan = "";
    message = encode_message_send("set-capacity-tcan",id_tcan,id_tcan,"GET",1,"tcan")
    client.send(message.encode('ascii'))

#Get status the list of tcans
def get_status_tcans():
    # message = encode_message_send("get-tcans","","","GET",1,"server")
    # client.send(message.encode('ascii'))
    
    # message = client.recv(1024).decode('ascii')
    # response = json.loads(message);
    if len(list_tcans) == 0:
        print(["NO TRASHCAN REGISTERED"])
    else:
        message = ""
        for i in list_tcans:
            message+=f'TRASHCAN ID: {i[0]}  CAPACITY: {i[2]}  LOCK: {"BLOCKED" if i[3] == "1" else "RELEASED"}\n'
    
        print(message)

# Change order the list of tcan
def change_order_list_tcan():
    if len(list_tcans) == 0:
        print(["NO TRASHCAN REGISTERED"])
    else:
        message = ""
        tcan_id = input('[CHOOSE THE ID THE TRASCAN]\n')
        for i in list_tcans:
            message+=f'TRASHCAN ID: {i[0]}  CAPACITY: {i[2]}  LOCK: {"BLOCKED" if i[3] == "1" else "RELEASED"}\n'
    
        message = encode_message_send("change-order-list",tcan_id,tcan_id,"PUT",1,"server")
        client.send(message.encode('ascii'))

        message_return = client.recv(1024).decode('ascii')

        print(json.loads(message_return)[message])

def decode_message_route(message):
    result = json.loads(message)

    return result["header"]["route"]

def encode_message_send(route,message,value,method,type,target):
    # se type igual a 0 é um send que responde uma requisição e de for 1 é um send que envia um requisição
    message = ""
    if type == 0:
        message = {
            "header":{
                "typeResponse": route,
                "target":target
            },
            "value": value,
            "message": message
        }
    else:
        message = {
            "header":{
                "method": method,
                "route": route,
                "target":target
            },
            "value": value,
            "message": message,
        }

    return json.dumps(message)

def update_list_tcans(list_tcansAux):

    if list_tcansAux.count(';') > 0:
        list = list_tcansAux.split(';')
    else:
        list = []
        list.append(list_tcansAux)

    message = ''
    for i in list:
        info_tcan = i.split(',')
        message+= f'ID: {info_tcan[0]}, CAPACITY: {info_tcan[1]}, LOCKED:: {info_tcan[2]}\n'

    return message
# Starting threads
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()