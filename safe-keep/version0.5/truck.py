import json
import socket
import threading

clientID = 'truck'

# Connection to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55556))

def receive():
    #if the message received from the server is 'ID' we send the ID 'truck' if it is any other message from the trashcan we just print it
    while True:
        try:
            message = json.loads(client.recv(1024).decode('ascii'))
            route = message["route"]
            if route == 'ID':
                client.send(clientID.encode('ascii'))
            else:
                print(f'{message}\n\n')
        except:
            print('[ERROR TRUCK!]')
            break

def write():
    #the message will be the input of the user
    while True:
        # message = '{}'.format(input(''))
        message = input('\n\n[THIS IS THE TRUCK INTERFACE, YOU CAN:]\n[ASK FOR THE STATUS OF THE TRASHCAN: INPUT "status"]\n[REMOVE THE TRASH FROM THE TRASHCAN: INPUT "dump"]\n\n')
        message_JSON = "{'message':'" + message + "'}"
        client.send(message_JSON.encode('ascii'))

# Starting threads
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()