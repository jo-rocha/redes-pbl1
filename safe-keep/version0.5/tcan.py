import json
import socket
import threading

clientID = 'tcan'

# Trashcan attributes
loadCapacity = 60
currentLoad = 0

# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55556))

def receive():
    global currentLoad
    while True:
        try:
            message = json.loads(client.recv(1024).decode('ascii'))
            route = message["route"]
            if route == 'ID':
                clientID_JSON = "{'ID':'"+ clientID  +"'}"
                client.send(clientID_JSON.encode('ascii'))
            elif route == 'dump':
                currentLoad = 0
                # sendMessage = f'<TRASHCAN STATUS: {str(currentLoad)}>'
                sendMessage = "{'status':'"+ str(currentLoad)  +"'}"
                client.send(sendMessage.encode('ascii'))
                print(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n')
            elif route == 'status':
                # sendMessage = f'<TRASHCAN STATUS: {str(currentLoad)}>'
                sendMessage = "{'status':'"+ str(currentLoad)  +"'}"
                client.send(sendMessage.encode('ascii'))
            elif route == 'hello':
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
            trashInput = input(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n\n')
            aux = int(trashInput) + currentLoad
            if aux > loadCapacity:
                input('\n\n[THE TRASHCAN CANNOT HOLD THIS AMOUNT OF TRASH. INPUT: "ok" TO RETURN]\n\n')
            else: currentLoad = aux
        else:
            input('\n\n[THE TRASHCAN IS FULL, YOU MUST WAIT FOR THE TRASHCAN TO BE EMPTIED]\n[INPUT: "ok" TO RELOAD THE STATUS OF THE TRASHCAN]\n\n')
        
        
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()
