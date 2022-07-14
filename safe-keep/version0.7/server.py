import socket
import threading
import constant
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

# Lida com as conexões dos clientes
def start():
    server.listen()
    print('[SERVER LISTENING...]')
    try:
        while(True):
            connection, address = server.accept()
            connection.send('ID'.encode('ascii'))# O server manda uma mensagem que funciona como um 'trigger' para que o cliente mande uma identificação (lixeira, caminhão ou admin)
            connectionID = connection.recv(1024).decode('ascii')
            print(f'[ESTABLISHED CONNECTION WITH {address}]')
            clients.append((connection, connectionID))
            # Agora que o cliente está conectado e guardado em clients[], eu preciso iniciar a thread para lidar com o enviar e receber
            # de messangens dos clientes
            if connectionID == 'tcan':
                thread = threading.Thread(target = handle_tcan, args = (connection,))
                thread.start()
            elif connectionID == 'truck':
                thread = threading.Thread(target = handle_truck, args = (connection,))
                thread.start()
    except:
        server.close()
        connection.close()

##
# Função responsável por lidar com a conexão dos clientes do tipo trashcan(lixeira)
##
def handle_tcan(connection,):
    unitID = assign_tcan(connection)
    try:
        while True:
            message = connection.recv(1024).decode('ascii')
            if message.startswith('status:'):# Se a lixeira foi esvaziada, ou se ela foi atualizada em seu volume de lixo a lista tem que ser atualizada
                message = message[7:]
                # Procura o index na lista de lixeiras do cliente atual para atualizar seu status
                index = 0
                for i in trashcans:
                    if i[0] == unitID:
                        break
                    index += 1
                trashcans[index][2] = message

                sort_ordered_list()
            else:
                print('receiving the wrong message')
    except:
        print('[ERROR TRASHCAN SERVER!]')
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
    trashcans.sort(key = lambda x: x[2], reverse = True)
    for i in trashcans:
        print(f'{i[0]}, {i[2]}')
    #lembrar de chamar send_to_truck() quando terminar de atualizar a lista


##
# Função responsável por lidar com a conexão dos clientes do tipo truck(caminhão)
##
def handle_truck(connection,):
    try:
        while True:
            message = connection.recv(1024).decode('ascii')
            send_to_trashcan(message)# teoricamente não vai precisar
            print('<message from truck>')
    except:
        print('[ERROR TRUCK SERVER!]')
        connection.close()

def send_to_truck(message):
    for i in clients:
        if i[1] == 'truck':
            truck = i[0]
            truck.send(message.encode('ascii'))
            break
    
# não vai ser usada
def send_to_trashcan(message):
    for i in clients:
        if i[1] == 'tcan':
            tcan = i[0]
            tcan.send(message.encode('ascii'))
            break
    

start()