import socket
import threading
import constant

clientID = 'truck'
currentLoad = 0

# Connection to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((constant.Host, constant.Port))

def receive():
    #if the message received from the server is 'ID' we send the ID 'truck' if it is any other message from the trashcan we just print it
    try:
        while True:
            message = client.recv(1024).decode('ascii')
            if message == 'ID':
                client.send(clientID.encode('ascii'))
            elif message.startswith('dumped:'): 
                message = message[7:]
                currentLoad = currentLoad + message
            elif message.startswith('list:'):
                message = message[5:]
                print(message)
            
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
            client.send(message.encode('ascii'))
    except:
        client.close()

# Starting threads
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()