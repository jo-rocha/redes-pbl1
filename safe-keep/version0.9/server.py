import socket
import threading
import constant
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
    connection.send('ID'.encode('ascii'))# O server manda uma mensagem que funciona como um 'trigger' para que o cliente mande uma identificação (lixeira, caminhão ou admin)
    connectionID = connection.recv(1024).decode('ascii')
    print(f'[ESTABLISHED CONNECTION WITH {address}]')
    clients.append((connection, connectionID))
    # Agora que o cliente está conectado e guardado em clients[], eu preciso iniciar a thread para lidar com o enviar e receber
    # de messangens dos clientes
    if connectionID == 'tcan':
        unitID = assign_tcan(connection)
        try:
            while True:
                message = connection.recv(1024).decode('ascii')
                if message.startswith('status:'):# Se a lixeira foi esvaziada, ou se ela foi atualizada em seu volume de lixo a lista tem que ser atualizada
                    message = message[7:]# tira o 'status:' da mensagem para ficar só o valor
                    # Procura o index na lista de lixeiras do cliente atual para atualizar seu status
                    index = 0
                    for i in trashcans:
                        if i[0] == unitID:
                            break
                        index += 1
                    trashcans[index][2] = message
                    sort_ordered_list()
                    #mandar lista pro caminhão
                elif message.startswith('dumped:'):# Se a lixeira foi esvaziada ela também manda uma mensagem com o tanto de lixo que ela tinha para poder enviar para atualizar o valor do caminhão
                    index = 0
                    for i in trashcans:
                        if i[0] == unitID:
                            break
                        index += 1
                    trashcans[index][2] = '0'
                    sort_ordered_list()
                    #no json adicionar na mensagem para o caminhão a quantidade de lixo esvaziada da lixeira que é o 'message'
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

##
# Essa função vai designar um ID único para cada lixeira conectada no servidor e colocá-la na lista de lixeiras. Depois ela vai retornar o itme que ela acabou
# de colocar na lixeira para facilitar a atualização do status da lixeira na função handle_tcan()
# param: Recebe o socket da lixeira que acabou de ser conectada
# return: Retorna o ID da lixeira para facilitar a busca da lixeira específica para a atualização de status em 'handle_tcan'
##
def assign_tcan(connection):
    unitID = str(len(trashcans))
    connection.send('status'.encode('ascii'))
    message = connection.recv(1024).decode('ascii')
    if message.startswith('status:'):
        status = message[7:]# Corta o início da mensagem que é 'status:'
        trashcans.append([unitID, connection, status])
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

# def send_to_truck(message):
#     for i in clients:
#         if i[1] == 'truck':
#             truck = i[0]
#             truck.send(message.encode('ascii'))
#             break
    
# # não vai ser usada
# def send_to_trashcan(message):
#     for i in clients:
#         if i[1] == 'tcan':
#             tcan = i[0]
#             tcan.send(message.encode('ascii'))
#             break
    

start()