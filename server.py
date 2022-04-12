import socket
import threading
import constant
import json
from operator import itemgetter

# host = '127.0.0.1'
# port = 55556
# Creating socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((constant.Host, constant.Port))

# List for clients 
clients = []
trashcans = []
orderedList = [] 
truck = None

# Lida com as conexões dos clientes
def start():
    server.listen()
    print('[SERVER LISTENING...]')
    try:
        while(True):
            connection, address = server.accept()
            thread = threading.Thread(target = handle_client, args = (connection, address))
            thread.start()
    except:
        server.close()
        connection.close()

##
# Função responśavel por lidar com o cliente assim que ele se conecta com o servidor
##
def handle_client(connection, address):
    message = encode_message_send("ID","","ID","GET",1)

    connection.send(message.encode('ascii'))
    
    connectionID = connection.recv(1024).decode('ascii')
    message_decode = json.loads(connectionID)
    
    connectionID = message_decode["value"]

    print(f'[ESTABLISHED CONNECTION WITH {address}]')
    clients.append((connection, connectionID))
    # Agora que o cliente está conectado e guardado em clients[], eu preciso iniciar a thread para lidar com o enviar e receber
    # de messangens dos clientes
    if connectionID == 'tcan':
        unitID = assign_tcan(connection)
        try:
            while True:
                message = connection.recv(1024).decode('ascii')
                message_response = decode_message_response(message)
                if message_response.startswith('status'):# Se a lixeira foi esvaziada, ou se ela foi atualizada em seu volume de lixo a lista tem que ser atualizada
                    message_decode = json.loads(message)
                    message = message_decode["value"]# Corta o início da mensagem que é 'status:'
                    # Procura o index na lista de lixeiras do cliente atual para atualizar seu status
                    index = 0
                    for i in trashcans:
                        if i[0] == unitID:
                            break
                        index += 1
                    trashcans[index][2] = message
                    sort_ordered_list()
                    
                    trashcansAux = []
                    for trashcan in trashcans:
                        trashcansAux.append(f'{trashcan[0]},{trashcan[2]},{trashcan[3]}')
                    message_list_tcans = '; '.join(trashcansAux)

                    sendMessage = encode_message_send('set-list-tcans',message_list_tcans,message_list_tcans,"PUT",1)
                    send_to_truck(sendMessage)
                    send_to_admin(sendMessage)    
                    #mandar lista pro caminhão e para o admin
                elif message_response.startswith('dumped'):# Se a lixeira foi esvaziada ela também manda uma mensagem com o tanto de lixo que ela tinha para poder enviar para atualizar o valor do caminhão
                    index = 0
                    for i in trashcans:
                        if i[0] == unitID:
                            break
                        index += 1
                    trashcans[index][2] = '0'
                    sort_ordered_list()
                    # trashcansAux = []
                    # for trashcan in trashcans:
                    #     trashcansAux.append([trashcan[0], trashcan[1], trashcan[2]])
                    # message_list_tcans = ', '.join(trashcansAux)
                    # print(message_list_tcans)
                    # sendMessage = encode_message_send('set-list-tcans',message_list_tcans,message_list_tcans,"PUT",1)
                    # send_to_truck(sendMessage)
                    # send_to_admin(sendMessage)    
                    # no json adicionar na mensagem para o caminhão a quantidade de lixo esvaziada da lixeira que é o 'message'
                elif message_response.startswith("released"):
                    message_decode = json.loads(message)
                    print(f'"[THE TRASHCAN IS {"BLOCKED" if message_decode["value"] == "1" else "RELEASED"}]"\n')
                elif message_response.startswith("get-tcans"):
                    pass
                else:
                    print('receiving the wrong message')
        except:
            print('[ERROR TRASHCAN SERVER!]')
            connection.close()
    elif connectionID == 'truck':
        truck = connection
        try:
            while True:
                message = connection.recv(1024).decode('ascii')
                print('<message from truck>')
        except:
            print('[ERROR TRUCK SERVER!]')
            connection.close()
    elif connectionID == 'admin':
        admin = connection
        try:
            while True:
                message = connection.recv(1024).decode('ascii')
                message_target = json.loads(message)["header"]["target"]
                
                if message_target == "tcan":
                    send_to_trashcan(message)
                
                elif message_target == "truck":
                    send_to_truck(message)
                
                elif message_target == "server":
                    
                    message_route = json.loads(message)["header"]["route"]
                    if(message_route == "get-tcans"):
                        
                        message_response = ""
                        for i in trashcans:
                            message_response +=f'"TRASHCAN ID:"{i[0]} + "CAPACITY: {i[2]}"\n'
                        
                        connection.send(message.encode('ascii'))
                    
                    elif(message_route == "change-order-list"):
                        tcan_id = json.loads(message)["value"]
                        index -1
                        for idx,i in trashcans:
                            if i[0] == tcan_id:
                                index = idx
                                break
                        message_return = "UNSPECIFIED OR UNKONWN TRASHCANS"
                        
                        if index > -1:
                            tcan_temp = trashcans[index]
                            trashcans.pop(index)
                            trashcans.insert(0,tcan_temp)
                            message_return = "ORDER UPDATED SUCCESSFULLY"
                        
                        message = encode_message_send("change-order-list",message_return,index,"",0)
                        connection.send(message.encode('ascii'))
                
                else: 
                    print('[unspecified or unknown client]')
                    print('<message from admin>')
        except:
            print('[ERROR ADMIN SERVER!]')
            connection.close()
##
# Essa função vai designar um ID único para cada lixeira conectada no servidor e colocá-la na lista de lixeiras. Depois ela vai retornar o itme que ela acabou
# de colocar na lixeira para facilitar a atualização do status da lixeira na função handle_tcan()
# param: Recebe o socket da lixeira que acabou de ser conectada
# return: Retorna o ID da lixeira para facilitar a busca da lixeira específica para a atualização de status em 'handle_tcan'
##
def assign_tcan(connection):
    unitID = str(len(trashcans))
    lock = False
    message = encode_message_send("status","","status","GET","1")
    connection.send(message.encode('ascii'))
    message = connection.recv(1024).decode('ascii')
    message_route = decode_message_response(message)
    if message_route.startswith('status'):
        message_decode = json.loads(message)
        status = message_decode["value"]# Corta o início da mensagem que é 'status:'
        trashcans.append([unitID, connection, status, lock])
    else: print('not getting the status of the trashcan')
    #retorna a posição em que este cliente foi colocado na lista de lixeiras para facilitar a atualização de seu status na função handle_tcan
    return unitID

##
# Essa função vai analisar a lista de lixeiras e fazer a ordenação de acordo com a quantidade de lixo que cada lixeira tem
##
def sort_ordered_list():
    trashcans.sort(key = lambda x: int(x[2]), reverse = True)
    for i in trashcans:
        print(f'\n{i[0]}, {i[2]}')
    #lembrar de chamar send_to_truck() quando terminar de atualizar a lista

def send_to_truck(message):
    for i in clients:
        if i[1] == 'truck':
            truck = i[0]
            truck.send(message)

def send_to_truck(message):
    for i in clients:
        if i[1] == 'truck':
            truck = i[0]
            truck.send(message.encode('ascii'))
            break

def send_to_admin(message):
    for i in clients:
        if i[1] == 'admin':
            admin = i[0]
            admin.send(message.encode('ascii'))
            break
    
# # não vai ser usada
def send_to_trashcan(message):
    tcan_id = json.loads(message)["value"]
    for i in trashcans:
        if i[0] == tcan_id:
            tcan = i[1]
            tcan.send(message.encode('ascii'))
            break
    
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

def decode_message_response(message):
    message = json.loads(message)

    return message["header"]["typeResponse"]


start()
