import socket
import threading

clientID = 'tcan'

# Trashcan attributes
loadCapacity = 60
currentLoad = 10

# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55556))

def receive():
    global currentLoad
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'ID':
                client.send(clientID.encode('ascii'))
            elif message == 'dump':
                currentLoad = 0
                client.send(currentLoad.encode('ascii'))
            elif message == 'status':
                client.send(currentLoad.encode('ascii'))
        except:
            print('An error has occurred!')
            break

def write():
    global currentLoad
    while True:
        trashInput = input('[IF YOU WANT TO THROW TRASH IN THE TRASHCAN INPUT THE AMOUNT OF TRASH:\n]')
        currentLoad = currentLoad + int(trashInput)
        print(currentLoad)
    
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()
