import socket
import threading
import constant
import json

clientID = 'truck'
currentLoad = 0
loadCapacity = 500
tcanList = None
listPrint = None

# Connection to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((constant.Host, constant.Port))

##
# Essa função vai ser responsável por lidar com as mensagens que o caminhão vai receber dos outros clientes através do servidor
##
def receive():
    global tcanList
    global listPrint
    global currentLoad 
    global loadCapacity
    # Se o servidor mandar a mensagem 'ID' o caminhão vai mandar uma mensagem identificado que tipo de cliente ele é. No caso, 'truck'
    try:
        while True:
            message = client.recv(1024).decode('ascii')
            messageDecode = json.loads(message)
            message = decode_message_route(message)

            if message['header']['route'] == 'ID':
                # client.send(clientID.encode('ascii'))
                sendMessage = encode_message_send('ID', clientID, clientID, '', 0)
                client.send(sendMessage.encode('ascii'))
            # Quando a lixeira esvazia e manda a mensagem com a quantidade de lixo que foi esvaziado, o servidor encaminha essa mensagem para o caminhão
            # e o caminhão adiciona a quantidade de lixo a sua carga. Se o caminhão chegar a quantidade limite ele esvazia sua carga na estação
            elif message['header']['route'] == 'dump':
                aux = currentLoad + message['value']
                if aux <= loadCapacity:
                    currentLoad = aux
                else:
                    #se a quantidade de lixo for passar a quantidade máxima do caminhão, o caminhão joga o lixo na estação
                    messageSend = encode_message_send('dump', 'dump', currentLoad, 1)
                    client.send(messageSend.encode('ascii'))
                    currentLoad = 0

            elif message['header']['route'] == 'set-list-tcans':#quando pega a lista ele faz a mensagem de rota e manda a rota para o admin
                tcanList, listPrint = organize_tcan_list(message['value'])
                if messageDecode['value2'] != None:#significa que a lixeira esvaziou e a quantidade de lixo foi enviada em value2
                    aux = currentLoad + messageDecode['value2']
                    if aux <= loadCapacity:
                        currentLoad = aux
                    else:
                        #se a quantidade de lixo for passar a quantidade máxima do caminhão, o caminhão joga o lixo na estação
                        messageSend = encode_message_send('dump', 'dump', currentLoad,'POST', 1)
                        client.send(messageSend.encode('ascii'))
                        currentLoad = 0
                
            else:
                print(f'{message}\n\n')
            

    except:
        print('[ERROR TRUCK!]')
        client.close()

def write():
    # A interface do caminhão mostra a quantidade de carga atual no caminhão, e a lixeira que está na rota dele. Que no caso é a primeira lixeira da lista de prioridade de lixeiras
    try:
        while True:
            # message = '{}'.format(input(''))
            if tcanList != None:
                tcanTarget = tcanList[0]
                tcanInfo = tcanTarget.split(',')
                targetMessage = f'ID: {tcanInfo[0]}, LOAD: {tcanInfo[1]}, LOCKED:: {tcanInfo[2]}'
                message = input(f'[THE TRUCK CURRENT LOAD IS {currentLoad}/{loadCapacity}\nAND IT IS HEADING TOWARDS THE TRASHCAN:{targetMessage}\n[CHOOSE AN OPERATION]\n1-SHOW TRASHCAN LIST\n2-TO UPDATE TRUCK STATUS\n\n\n\n\n')
                if message == '1':
                    print(f'####################################\n       LIST OF TRASHCANS\n####################################\n{listPrint}\n####################################\n')
                elif message == '2':
                    pass
            else:
                input(f'[THE TRUCK CURRENT LOAD IS {currentLoad}/{loadCapacity}]\n[THERE IS NO CONNECTED TRASHCAN YET. INPUT "OK" TO UPDATE STATUS]\n\n\n\n')
    except:
        print('error writing')
        client.close()

def decode_message_route(message):
    result = json.loads(message)

    return result

#Organiza a lista de lixeiras em um padrão para ser mostrado na interface do caminhão, com o ID, a quantidade de lixo, e a informação de se a lixeira está trancada ou não
def organize_tcan_list(list_tcansAux):
    if list_tcansAux.count(';') > 0:
        list = list_tcansAux.split(';')
    else:
        list = []
        list.append(list_tcansAux)

    message = ''
    for i in list:
        info_tcan = i.split(',')
        message+= f'ID: {info_tcan[0]}, LOAD: {info_tcan[1]}, LOCKED:: {info_tcan[2]}\n'

    return list, message

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

# Starting threads
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()