import socket
import threading

host = '127.0.0.1'
port = 55556
# Creating socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

# List for clients 
clients = []

# Handles the connections with new clients
def start():
    server.listen()
    print('[SERVER LISTENING...]')
    while(True):
        connection, address = server.accept()
        connection.send('ID'.encode('ascii'))# Server sends a message to trigger the client identifyig itself
        connectionID = connection.recv(1024).decode('utf-8')
        print(f'[ESTABLISHED CONNECTION WITH {address}]')
        clients.append((connection, connectionID))
        # Now that the client is connected and appended in the clients list, I need to start the thread to handle the sending and receiving
        # messages of the client
        if connectionID == 'tcan':
            thread = threading.Thread(target = handle_tcan, args = (connection, address))
            thread.start()
        elif connectionID == 'truck':
            thread = threading.Thread(target = handle_truck, args = (connection, address))
            thread.start()

def handle_tcan(connection, address):
    try:
        message = connection.recv(1024).decode('ascii')
        send_to_truck(message)
    except:
        print('an error has occurred')

def handle_truck(connection, address):
    try:
        message = connection.recv(1024).decode('ascii')
        send_to_trashcan(message)
    except:
        print('and error has occurred')

def send_to_truck(message):
    for i in clients:
        if i[1] == 'truck':
            truck = i[0]
            break
    truck.send(message)
def send_to_trashcan(message):
    for i in clients:
        if i[1] == 'tcan':
            tcan = i[0]
            break
    tcan.send(message)

start()