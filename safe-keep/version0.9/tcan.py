import socket
import threading
import constant

clientID = 'tcan'

# Trashcan attributes
loadCapacity = 60
currentLoad = 0

# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((constant.Host, constant.Port))

def receive():
    global currentLoad
    try:
        while True:
            message = client.recv(1024).decode('ascii')
            if message == 'ID':
                client.send(clientID.encode('ascii'))
            elif message == 'dump':
                currentLoad = 0
                sendMessage = f'<TRASHCAN STATUS: {str(currentLoad)}>'
                client.send(sendMessage.encode('ascii'))
                print(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n')
            elif message == 'status':
                sendMessage = f'status:{str(currentLoad)}'
                client.send(sendMessage.encode('ascii'))
            elif message == 'hello':
                print(message)
    except:
        print('[ERROR TRASHCAN]')
        client.close()
        return None

def write():
    global currentLoad
    try:
        while True:
            # trashInput = input('[IF YOU WANT TO THROW TRASH IN THE TRASHCAN INPUT THE AMOUNT OF TRASH:]\n')
            # currentLoad = currentLoad + int(trashInput)
            # print(currentLoad)
            # ##added
            # client.send('message from the tcan'.encode('ascii'))
            trashInput = input(f'\n\n[THE TRASHCAN CURRENT LOAD IS: {currentLoad}/{loadCapacity}]\n[INPUT THE AMOUNT OF TRASH YOU WANT TO THROW AT THE TRASHCAN:]\n\n')
            if trashInput != 'dump':
                if currentLoad < loadCapacity:
                    aux = int(trashInput) + currentLoad
                    if aux > loadCapacity:
                        input('[THE TRASHCAN CANNOT HOLD THIS AMOUNT OF TRASH. INPUT: "ok" TO RETURN]\n\n')
                    else: 
                        currentLoad = aux
                        client.send(f'status:{str(currentLoad)}'.encode('ascii'))
                else:
                    print("""######################################################################\n#[THE TRASHCAN IS FULL, YOU MUST WAIT FOR THE TRASHCAN TO BE EMPTIED]#\n######################################################################
                    """)
            else:
                toTruck = currentLoad # Guarda uma auxiliar 'toTruck' para quando a lixeira esvaziar mandar a carga para o caminhão
                currentLoad = 0
                client.send(f'dumped:{str(toTruck)}'.encode('ascii'))
    except:
        client.close()
        return None
        
        
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()
