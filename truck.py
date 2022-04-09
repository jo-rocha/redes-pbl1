import socket
import threading
import constant
import json
clientID = 'truck'

# Connection to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((constant.Host, constant.Port))

def receive():
    #if the message received from the server is 'ID' we send the ID 'truck' if it is any other message from the trashcan we just print it
    try:
        while True:
            message = client.recv(1024).decode('ascii')
            messageRoute = decode_message_route(message)
            if messageRoute == 'ID':
                sendMessage = encode_message_send("ID",clientID,clientID,"",0)
                client.send(sendMessage.encode('ascii'))
                # client.send(clientID.encode('ascii'))
            else:
                print(f'{message}\n\n')
    except:
        print('[ERROR TRUCK!]')
        client.close()

def write():
    #the message will be the input of the user
    try:
        while True:
            # message = '{}'.format(input(''))
            message = input('\n\n[THIS IS THE TRUCK INTERFACE, YOU CAN:]\n[ASK FOR THE STATUS OF THE TRASHCAN: INPUT "status"]\n[REMOVE THE TRASH FROM THE TRASHCAN: INPUT "dump"]\n\n')
            sendMessage = encode_message_send(message,message,"","GET",1)
            client.send(sendMessage.encode('ascii'))
            # client.send(message.encode('ascii'))
    except:
        client.close()

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


# Starting threads
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()