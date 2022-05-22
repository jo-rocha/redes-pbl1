# Responsável por representar o cliente do tipo administrador

import socket
import threading
import constant
import json

clientID = 'admin'
list_tcans = []
#Criando conexão com o servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((constant.Host, constant.Port))

# Função responsável por receber e tratar as requisições solicitadas para o administrador
def receive():
    while True:
        try:
            # Decodifica a mensagem em busca da operação que será realizada
            message = client.recv(1024).decode('ascii')
            messageRoute = decode_message_route(message)
            
            # Retorna o tipo do cliente, nesse caso seria admin
            if messageRoute == 'ID':
                sendMessage = encode_message_send("ID",clientID,clientID,"",0,"")
                client.send(sendMessage.encode('ascii'))
            
            # Retorna a lista de lixeiras já ordenadas
            elif messageRoute == 'get-list-tcan':
                sendMessage = encode_message_send("trashcan-list",sendMessage,"","",0,"")
                client.send(sendMessage.encode('ascii'))
            
            # Atualiza a lista de lixeiras. Essa requisição é chamada quando ocorre alguma alteração na lista de lixeiras
            elif messageRoute == 'set-list-tcans':
                messageResponse = json.loads(message)["value"]
                messageResponse = update_list_tcans(messageResponse)
                print("[TRASH CANS LIST UPDATED]")
                print(messageResponse)
        except:
            print('[ERROR ADMIN!]')
            break

# Função responsável por monitorar as solicitações do usuário, e mandar as solicitações para o servidor e o mesmo realizar o comando do usuário
def write():
    controle = 1
    try:
        while True:
            if controle == 1:
                request = input('[CHOOSE AN OPERATION]\n1-CHANGE STATUS TRASHCAN\n2-CHANGE CAPACITY TRASHCAN\n3-GET STATUS TRASHCANS\n4-CHANGE ORDER LIST TRASHCANS\n5-CLOSE\n\n\n\n\n')
                # Muda o status da lixeira para bloqueada ou liberada
                if request == "1":
                    change_status_tcan()
                elif request == "2":
                    change_capacity_tcan()
                # Mostrar estado atual das lixeiras
                elif request == "3":
                    get_status_tcans()
                # Muda a prioridade de uma lixeira da lista de coleta das lixeiras
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
    except:
        print("CLOSING APPLICATION...")
        client.close()
        return None

# Função responsável por mudar o estado das lixeiras, mandando uma solicitação de bloqueio para o servidor (blocked or released)
def change_status_tcan():
    if len(list_tcans) == 0:
        print("[NO TRASHCAN REGISTERED]")
    else:
        # Indica quais são as lixeiras cadastrados no servidor
        message = ""
        for i in list_tcans:
            info_tcan = i.split(',')
            message+=f'TRASHCAN ID: {info_tcan[0]}  CAPACITY: {info_tcan[1]}  LOCK: {"BLOCKED" if info_tcan[2] == "1" else "RELEASED"}\n'
    
        print(message)
        message = "set-block"
        # Usuário escolhe o ID da lixeira que será atualizada e o mesmo é enviado para o servidor
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

# Função responsável por retornar o estado atual das lixeiras cadastradas no servidor
def get_status_tcans():
    # Indica as lixerias cadastradas no servidor
    if len(list_tcans) == 0:
        print(["NO TRASHCAN REGISTERED"])
    else:
        message = ""
        for i in list_tcans:
            info_tcan = i.split(',')
            message+=f'TRASHCAN ID: {info_tcan[0]}  CAPACITY: {info_tcan[1]}  LOCK: {"BLOCKED" if info_tcan[2] == "1" else "RELEASED"}\n'
    
        print(message)

# Função responsável por mudar a prioridade de coleta das lixeiras
def change_order_list_tcan():
    if len(list_tcans) == 0:
        print("[NO TRASHCAN REGISTERED]")
    else:
        message = ""
        for i in list_tcans:
            info_tcan = i.split(',')
            message+=f'TRASHCAN ID: {info_tcan[0]}  CAPACITY: {info_tcan[1]}  LOCK: {"BLOCKED" if info_tcan[2] == "1" else "RELEASED"}\n'
    
        print(message)
        tcan_id = input('\n\n\n[CHOOSE THE ID THE TRASCAN]\n\n\n')
        
        message = encode_message_send("change-order-list",tcan_id,tcan_id,"PUT",1,"server")
        client.send(message.encode('ascii'))

# Função responsável por decodificar a mensagem recebida pelo cliente e obter a rota solicitada pela requisição.
def decode_message_route(message):
    # Transforma a mensagem recebida( no formato JSON) em um dicionario
    result = json.loads(message)

    return result["header"]["route"]

# Função responsável por montar a estrutura da mensagem que será enviada para os clientes/servidor. Implementando o formato JSON.
def encode_message_send(route,message,value,method,type,target):
    # se type igual a 0 é um envio que responde uma requisição e se for 1 é um envio de uma requisição
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

# Função responsável por decodificar a mensagem que é recebida quando a rota de atualizar a lista de lixeiras é chamada
def update_list_tcans(list_tcansAux):
    list = ''
    # Separa as lixeiras 
    if list_tcansAux.count(';') > 0:
        list = list_tcansAux.split(';')
    else:
        list = []
        list.append(list_tcansAux)
    
    message = ''
    list_tcans.clear()
    for i in list:
        list_tcans.append(i)
        # Separa os dados de uma lixeira
        info_tcan = i.split(',')
        # print(f'ID: {info_tcan[0]}, CAPACITY: {info_tcan[1]}, LOCKED:: {info_tcan[2]}\n')
        message+= f'ID: {info_tcan[0]}, CAPACITY: {info_tcan[1]}, LOCKED:: {info_tcan[2]}\n'

    return message


# Iniciando threads
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()