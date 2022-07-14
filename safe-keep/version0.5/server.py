import json
import socket
import threading

host = '26.241.233.114'
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
        connection.send('{"route":"ID"}'.encode('ascii'))# Server sends a message to trigger the client identifyig itself
        connectionID = decode_json(connection.recv(1024).decode('ascii'))
        print(f'[ESTABLISHED CONNECTION WITH {address}]')
        clients.append((connection, connectionID))
        # Now that the client is connected and appended in the clients list, I need to start the thread to handle the sending and receiving
        # messages of the client
        if connectionID["ID"] == 'tcan':
            thread = threading.Thread(target = handle_tcan, args = (connection,))
            thread.start()
        elif connectionID["ID"] == 'truck':
            thread = threading.Thread(target = handle_truck, args = (connection,))
            thread.start()

def handle_tcan(connection,):
    while True:
        try:
            message = connection.recv(1024).decode('ascii')
            ##added
            print('<message from tcan>')
            send_to_truck(message)
        except:
            print('[ERROR TRASHCAN SERVER!]')

def handle_truck(connection,):
    while True:
        try:
            message = connection.recv(1024).decode('ascii')
            send_to_trashcan(message)
            print('<message from truck>')
        except:
            print('[ERROR TRUCK SERVER!]')

def send_to_truck(message):
    for i in clients:
        if i[1] == 'truck':
            truck = i[0]
            truck.send(message.encode('ascii'))
            break
    
def send_to_trashcan(message):
    for i in clients:
        if i[1] == 'tcan':
            tcan = i[0]
            tcan.send(message.encode('ascii'))
            break

def decode_json(self,message):
    return json.loads(message)

start()