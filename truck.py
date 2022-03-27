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
            message = client.recv(1024).decode('ascii')
            if message == 'ID':
                client.send(clientID.encode('ascii'))
            else:
                print(message)
        except:
            print('An error has occurred!')
            break

def write():
    #the message will be the input of the user
    while True:
        message = '{}'.format(input(''))
        client.send(message.encode('ascii'))

# Starting threads
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()