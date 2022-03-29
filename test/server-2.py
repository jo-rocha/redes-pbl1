import socket
import threading
# Connection Data
host = '127.0.0.1'
port = 55556
# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []

# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client[0].send(message)

#removed
# # Handling Messages From Clients
# def handle(client):
#     while True:
#         try:
#             # Broadcasting Messages
#             message = client.recv(1024)
#             broadcast(message)
#         except:
#             # Removing And Closing Clients
#             index = clients.index(client)
#             clients.remove(client)
#             client.close()
#             broadcast('{} left!'.format(clients[index][1]).encode('ascii'))
#             break
#removed

#Handlign messages from trashcans
def handle_tcan(client):
    #Finding the truck client for the trashcan to send messages to 
    for i in clients:
        if i[1] == 'truck':
            truck = i[0]
            break

    while True:
        try:
            # Broadcasting Messages
            message = client[0].recv(1024)
            truck.send(message)
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client[0].close()
            broadcast('{} left!'.format(clients[index][1]).encode('ascii'))
            break

#Handlign messages from trucks
def handle_truck(client):
    #Finding the trashcan client for the truck to send messages to 
    for i in clients:
        print(i[1])
        # if i[1] == 'tcan':
        #     tcan = i[0]
        #     break
    while True:
        try:
            # Broadcasting Messages
            message = client[0].recv(1024)
            broadcast("hello".encode('ascii'))
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client[0].close()
            broadcast('{} left!'.format(clients[index][1]).encode('ascii'))
            break

# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('ID'.encode('ascii'))
        clientID = client.recv(1024).decode('ascii')
        new_client = (client, clientID)#tuple to be placed in the clients array
        clients.append(new_client)

        # Print And Broadcast Nickname
        print("clientID is {}".format(clientID))
        broadcast("{} joined!".format(clientID).encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))

        # Start Handling Thread For Client
        if clientID == 'tcan':    
            thread = threading.Thread(target=handle_tcan, args=(new_client,))
            thread.start()
        elif clientID == 'truck':    
            thread = threading.Thread(target=handle_truck, args=(new_client,))
            thread.start()

        #removed
        # thread = threading.Thread(target=handle, args=(client,))
        # thread.start()
        #removed

receive()


