import socket
import threading

clientID = 'tcan'

# Trashcan attributes
loadCapacity = 60
currentLoad = 0

# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('26.241.233.114', 55556))

def receive():
    global currentLoad
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'ID':
                client.send(clientID.encode('ascii'))
            elif message == 'dump':
                print('hi')
                currentLoad = 0
                client.send(str(currentLoad).encode('ascii'))
            elif message == 'status':
                client.send(str(currentLoad).encode('ascii'))
            elif message == 'hello':
                print(message)
        except:
            print('[ERROR TRASHCAN]')
            break

def write():
    global currentLoad
    while True:
        # trashInput = input('[IF YOU WANT TO THROW TRASH IN THE TRASHCAN INPUT THE AMOUNT OF TRASH:]\n')
        # currentLoad = currentLoad + int(trashInput)
        # print(currentLoad)
        # ##added
        # client.send('message from the tcan'.encode('ascii'))
        if currentLoad < loadCapacity:
            trashInput = input(f'[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n')
            aux = int(trashInput) + currentLoad
            if aux > loadCapacity:
                input('[THE TRASHCAN CANNOT HOLD THIS AMOUNT OF TRASH]')
            else: currentLoad = aux
        else:
            input('[THE TRASHCAN IS FULL, YOU MUST WAIT FOR THE TRASHCAN TO BE EMPTIED]\n[TYPE "ok" TO RELOAD THE STATUS OF THE TRASHCAN]')
        
        
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()
