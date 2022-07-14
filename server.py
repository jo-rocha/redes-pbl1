# Responsável por representar o servidor da aplicação
from itertools import count
import socket
import threading
import constant
import json
from operator import itemgetter

# host = '26.241.233.114'
# port = 55556
# Creating socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((constant.Host, constant.Port))

# List for clients 
clients = []
trashcans = []
orderedList = []
order_priority = 0
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
    global order_priority
    message = encode_message_send("ID","","ID","GET",1)

    connection.send(message.encode('ascii'))
    
    connectionID = connection.recv(1024).decode('ascii')
    message_decode = json.loads(connectionID)
    
    connectionID = message_decode["value"]

    print(f'[ESTABLISHED CONNECTION WITH {address}]')
    clients.append((connection, connectionID))
    # Agora que o cliente está conectado e guardado em clients[], eu preciso iniciar a thread para lidar com o enviar e receber
    # de messangens dos clientes
    # Caso o cliente conectado seja do tipo lixeira
    if connectionID == 'tcan':
        unitID = assign_tcan(connection)
        try:
            while True:
                message = connection.recv(1024).decode('ascii')
                # Decodifica a mensagem recebida para indenrificar qual foi a requisição solicitada para o servidor
                message_response = decode_message_response(message)
                if message_response.startswith('status'):# Se a lixeira foi esvaziada, ou se ela foi atualizada em seu volume de lixo a lista tem que ser atualizada
                    message_decode = json.loads(message)
                    message = message_decode["value"]
                    # Procura o index na lista de lixeiras do cliente atual para atualizar seu status
                    index = 0
                    for i in trashcans:
                        if i[0] == unitID:
                            break
                        index += 1
                    trashcans[index][2] = message
                    # Atualiza a ordem de prioridade
                    if int(trashcans[index][4]) < 0:
                        trashcans[index][4] = -1
                    sort_ordered_list()
                    
                    # Como a lista de lixeiras foi atualizada os clientes precisam saber dessa alteração, por isso a nova lista é enviada para o caminhão e para o administrador
                    trashcansAux = []
                    for trashcan in trashcans:
                        trashcansAux.append(f'{trashcan[0]},{trashcan[2]},{trashcan[3]}')
                    message_list_tcans = '; '.join(trashcansAux)

                    sendMessage = encode_message_send('set-list-tcans',message_list_tcans,message_list_tcans,"PUT",1)
                    send_to_truck(sendMessage)
                    send_to_admin(sendMessage)

                elif message_response.startswith('dumped'):# Se a lixeira foi esvaziada ela também manda uma mensagem com o tanto de lixo que ela tinha para poder enviar para atualizar o valor do caminhão
                    message_decode = json.loads(message)
                    index = 0
                    for i in trashcans:
                        if i[0] == unitID:
                            break
                        index += 1
                    # Esvazia a lixeira
                    trashcans[index][2] = '0'
                    # Como a lixeira é esvaziada a mesma é enviada para o final da lista
                    trashcans[index][4] = -2
                    sort_ordered_list()

                    # Como a lista de lixeiras foi atualizada os clientes precisam saber dessa alteração, por isso a nova lista é enviada para o caminhão e para o administrador
                    trashcansAux = []
                    for trashcan in trashcans:
                        trashcansAux.append(f'{trashcan[0]},{trashcan[2]},{trashcan[3]}')
                    message_list_tcans = '; '.join(trashcansAux)
                    print(message_list_tcans)
                    sendMessage = encode_message_send('set-list-tcans',message_list_tcans,message_list_tcans,"PUT",1, message_decode['value2'])
                    send_to_truck(sendMessage)
                    send_to_admin(sendMessage)    

                # Retorno da lixeira quando é requisitado o bloqueio da mesma
                elif message_response.startswith("released"): 
                    
                    # Retorna o estado atual da lixeira
                    message_decode = json.loads(message)
                    print(f'"[THE TRASHCAN IS {"BLOCKED" if message_decode["value"] == "1" else "RELEASED"}]"\n')
                    
                    # Como a lista de lixeiras foi atualizada os clientes precisam saber dessa alteração, por isso a nova lista é enviada para o caminhão e para o administrador
                    trashcansAux = []
                    for trashcan in trashcans:
                        trashcansAux.append(f'{trashcan[0]},{trashcan[2]},{trashcan[3]}')
                    message_list_tcans = '; '.join(trashcansAux)
                    print(message_list_tcans)
                    sendMessage = encode_message_send('set-list-tcans',message_list_tcans,message_list_tcans,"PUT",1)
                    send_to_truck(sendMessage)
                    send_to_admin(sendMessage)
                elif message_response.startswith("get-tcans"):
                    pass
                else:
                    print('receiving the wrong message')
        except:
            print('[ERROR TRASHCAN SERVER!]')
            connection.close()
    
    # Caso o cliente conectado seja do tipo caminhão
    elif connectionID == 'truck':
        truck = connection
        try:
            while True:
                message = connection.recv(1024).decode('ascii')
                print('<message from truck>')
        except:
            print('[ERROR TRUCK SERVER!]')
            connection.close()
    
    # Caso o cliente conectado seja do tipo administrador
    elif connectionID == 'admin':
        admin = connection
        try:
            while True:
                message = connection.recv(1024).decode('ascii')
                message_target = json.loads(message)["header"]["target"]
                # Verifica para qual cliente a solicitação do aministrador é destinada
                if message_target == "tcan":
                    # Envia a solicitação para a lixeira
                    send_to_trashcan(message)
                    route = message_target = json.loads(message)["header"]["route"]
                    # Caso seja a solicitação de mudar o esrado de uma lixeira, o valor é atualizado na lista de lixeiras do servidor
                    if route == 'set-block':
                        tcan_id = message_target = json.loads(message)["value"]
                        for i in trashcans:
                            if i[0] == tcan_id:
                                i[3] = "0" if i[3] == "1" else "1"
                                break
                
                elif message_target == "truck":
                    send_to_truck(message)
                
                elif message_target == "server":
                    
                    message_route = json.loads(message)["header"]["route"]
                    # Retorna a lista das lixeiras para o administrador
                    if(message_route == "get-tcans"):
                        
                        message_response = ""
                        for i in trashcans:
                            message_response +=f'"TRASHCAN ID:"{i[0]} + "CAPACITY: {i[2]}"\n'
                        
                        connection.send(message.encode('ascii'))
                    # Muda a prioridade de uma lixeira para a mesma ir para o topo da lista de coleta
                    elif(message_route == "change-order-list"):
                        
                        tcan_id = json.loads(message)["value"]
                        index = 0
                        
                        for i in trashcans:
                            if i[0] == tcan_id:
                                break
                            else:
                                index = index + 1
                        
                        message_return = "UNSPECIFIED OR UNKONWN TRASHCANS"
                        print("Encontrou lixeira")
                        
                        # Se encontrou a lixeira indicada na requisição, a mesma é adicionada ao topo da lista
                        if index > -1:
                            tcan_temp = trashcans[index]
                            trashcans.pop(index)
                            # order_priotity guarda o maior grau de prioridade de uma lixeira
                            tcan_temp[4] = order_priority + 1
                            trashcans.insert(0,tcan_temp)
                            message_return = "ORDER UPDATED SUCCESSFULLY"
                        
                        print("Entrou rota servidor")

                        # retorna para o adimistrador a lista de lixeiras atualizada
                        trashcansAux = []
                        message_list_tcans = ''
                        for trashcan in trashcans:
                            trashcansAux.append(f'{trashcan[0]},{trashcan[2]},{trashcan[3]}')
                            message_list_tcans = '; '.join(trashcansAux)
                        
                        message = encode_message_send("set-list-tcans",message_return,message_list_tcans,"",1)
                        connection.send(message.encode('ascii'))
                        # send_to_truck(sendMessage)
                        # order_priority = order_priority + 1
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
    ordem = - 1
    message = encode_message_send("status","","status","GET","1")
    connection.send(message.encode('ascii'))
    message = connection.recv(1024).decode('ascii')
    message_route = decode_message_response(message)
    if message_route.startswith('status'):
        message_decode = json.loads(message)
        status = message_decode["value"]# Corta o início da mensagem que é 'status:'
        trashcans.append([unitID, connection, status, lock,-1])
    else: print('not getting the status of the trashcan')
    #retorna a posição em que este cliente foi colocado na lista de lixeiras para facilitar a atualização de seu status na função handle_tcan
    return unitID

##
# Essa função vai analisar a lista de lixeiras e fazer a ordenação de acordo com a quantidade de lixo que cada lixeira tem
##
def sort_ordered_list():
    # Ordenação pela quantidade de lixo
    trashcans.sort(key = lambda x: int(x[2]), reverse = True)
    # Ordenação pela ordem de prioridade
    trashcans.sort(key = lambda x: int(x[4]), reverse = True)
    message =''
    for i in trashcans:
        # print(f'\n{i[0]}, {i[2]}')
        message+= f'ID: {i[0]}, LOAD: {i[1]}, LOCKED:: {i[2]}\n'
    print(f'####################################\n       LIST OF TRASHCANS\n####################################\n{message}\n####################################\n')
    #lembrar de chamar send_to_truck() quando terminar de atualizar a lista

# Função responsável por enviar uma mensagem para o caminhão
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

# Função responsável por enviar uma mensagem para o administrador
def send_to_admin(message):
    for i in clients:
        if i[1] == 'admin':
            admin = i[0]
            admin.send(message.encode('ascii'))
            break
    
# Função responsável por enviar uma mensagem para uma lixeira especifica
def send_to_trashcan(message):
    tcan_id = json.loads(message)["value"]
    for i in trashcans:
        if i[0] == tcan_id:
            tcan = i[1]
            tcan.send(message.encode('ascii'))
            break

# Função responsável por decodificar a mensagem recebida pelo cliente e obter a rota solicitada pela requisição.
def decode_message_route(message):
    result = json.loads(message)

    return result["header"]["route"]

# Função responsável por montar a estrutura da mensagem que será enviada para os clientes/servidor. Implementando o formato JSON.
def encode_message_send(route,message,value,method,type, value2 = None):
        # se type igual a 0 é um envio que responde uma requisição e se for 1 é um envio de uma requisição
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

# Função responsável por decodificar a mensagem recebida pelo cliente e obter a rota solicitada pelo retorno da requisição.
def decode_message_response(message):
    message = json.loads(message)

    return message["header"]["typeResponse"]


start()
