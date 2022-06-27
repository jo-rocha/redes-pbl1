# Comandos para startar a api
# Na primeira vez que for rodar o arquivo
# $env:FLASK_ENV = "development"
# $env:FLASK_APP = "api"
# 
# flask run
from flask import Flask
from flask import request
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs
import socket
import threading

app = Flask(__name__)

# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('26.241.233.14', 8080))

@app.route('/list-tcans')
def list_tcans():
    arquivo = open("listOfTcans.txt", "r")
    args = request.args
    number_lixeiras = int(args.get('number'))
    id_sector = int(args.get('sector'))
    tcans = arquivo.readlines()
    # tcans = []
    tcans_temp = ''
    # Recuperar informações via socket
    index = 0
    for tcan in tcans:
        tcans_temp += str(tcan) + '|'
        
        if(index == (number_lixeiras-1)):
            break

        index = index + 1 
    arquivo.close()
    aux_len = len(tcans_temp)
    aux_len = aux_len - 1
    tcans_temp = tcans_temp[0:aux_len]
    return str(tcans_temp) 

@app.route('/dump-tcan')
def list_tcans():

    args = request.args
    number_lixeiras = int(args.get('number'))
    id_sector = int(args.get('sector'))

@app.route('/get-sectores')
def get_sectores():
    # Retornar setores cadastrados no sistema
    pass

@app.route('/get-tcans')
def get_tcans():
    # Retonar as lixeiras cadastradas no sistema
    pass

@app.route('/get-tcan')
def get_tcan():
    # Retonar as lixeiras cadastradas no sistema
    pass

def receive():
    global currentLoad
    global lock
    global ordem
    try:
        while True:
            message = client.recv(1024).decode('ascii')
            messageRoute = decode_message_route(message)

            # Assim que o client se conecta com o servidor, o servidor manda uma mensagem 'ID', e assim o cliente entende que ele tem que mandar uma mensagem identificando
            # que tipo de cliente ele é (caminhão, lixeira ou admin)
            if messageRoute == 'ID':
                sendMessage = encode_message_send("ID",clientID,clientID,"",0)
                client.send(sendMessage.encode('ascii'))
            
            elif messageRoute == 'dump':
                currentLoad = 0
                sendMessage = encode_message_send("TRASHCAN STATUS",sendMessage,currentLoad,"",0)
                client.send(sendMessage.encode('ascii'))
                if int(ordem) < 0:
                    ordem = -2
                print(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{0}]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n')
            
            elif messageRoute == 'status':
                sendMessage = encode_message_send("status",currentLoad,currentLoad,"",0)
                client.send(sendMessage.encode('ascii'))
            
            elif messageRoute == 'set-block':
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
            # O input do usuário pode ser um valor de lixo para ser adicionado na lixeira, ou 'dump' que é para esvaziar a lixeira.
            # Se o input não for dump, a lixeira vai checar se a capacidade do input cabe na lixeira, e se ela está trancada. Se todas as requisições forem cumpridas
            # o valor do input é adicionado a lixeira, e uma mensagem é enviada para o servidor com a nova quantidade de lixo da lixeira para a lista de lixeiras do 
            # servidor ser atualizada
            trashInput = input(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{0} AND THE TRASHCAN IS {"BLOCKED" if lock == "1" else "RELEASED"} ]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n\n')
            if trashInput != 'dump':
                if currentLoad < 0:
                    aux = int(trashInput) + currentLoad
                    if aux > 0:
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
            # Se o input for 'dump' uma mensagem é enviada par o servidor com a quantidade atual da lixeira, e também é enviado a quantidade de lixo que foi esvaziada
            # para o caminhão atulizar sua quantidade de lixo
            else:
                toTruck = currentLoad # Guarda uma auxiliar 'toTruck' para quando a lixeira esvaziar mandar a carga para o caminhão
                currentLoad = 0
                sendMessage = encode_message_send("dumped","dumped",currentLoad,"POST",0, toTruck)
                if int(ordem) < 0:
                    ordem = -2
                client.send(sendMessage.encode('ascii'))
    except:
        client.close()
        return None

def decode_message_route(message):
    result = json.loads(message)

    return result["header"]["route"]

def encode_message_send(route,message,value):
    # se type igual a 0 é um send que responde uma requisição e de for 1 é um send que envia um requisição
    message = {
        "header":{
            "route": route,
        },
        "value": value,
        "message": message,
    }

    return json.dumps(message)  

receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()
