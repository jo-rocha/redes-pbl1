from contextlib import nullcontext
import socket
import threading
import time

host = '127.0.0.1'#localhost 
port = 55555
##
#theoretically this cannot exist within the server, but I don't know how to do it wihtout it yet
truck = []
tcans = []
admin = []
##
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#this creates an internet socket with the tcp protocol

server.bind((host, port))#binding the socket with its ip and port addresses

def handle_truck(client, address):
    try:
        #the truck sends a message that can be either 'dump' in which the trashcan dumps all it's trash, or 'status' where the trashcan will send it's status
        #and the server passes that message to the trashcan
        message = client.recv(1024).decode('utf-8')
        tcan = tcans[0]#right now I'm doing it with only one trashcan because I still don't know how we're going to handle all the trashcans
        tcan.send(message.encode('utf-8'))

    except:
        pass

def handle_tcan(client, address):
    try:
        #in the future the admin might be able to ask someting of the trashcan, but right now, the only message the trashcan will get is a message 
        #from the garbage truck, and depending on the message it will answer with it's status, so it will only send messages to the garbage truck
        message = client.recv(1024).encode('utf-8')
        truck = truck[0]
        truck.send(message.encode('utf-8'))
    except:
        pass

def handle_admin(client, address):
    pass

#in a situation for example, where the truck wants to dump the trash from a trashcan, it is going to send a message to server
#that is going to be handled by 'handle_truck' and 'handle_truck' is going to call broadcast, to pass the message to the desired 
#traschan, and broadcast is going to look for the destination and send the message
def broadcast(message):
    pass

def start():
    print('[SERVER LISTENING...]\n')
    server.listen()
    while True:
        client, address = server.accept()#awaits a connection with a client, and returns the client connection and it's address

        #Now after there is a connection established, the client can either be a truck or a traschan or the admin. In each situations
        #the client would be better handled by different functions, so I should identify which type of client it is 
        print(f"[NEW CONNECTION WITH {address}]\n")
        client.send('[CONNECTION ESTABLISHED WITH THE SERVER]\n'.encode('utf-8'))
        clientID = client.recv(1024).decode('utf-8')#the idea is that the client is going to automatically send a message identifying himself
                                                    #once it connects to the server
        if clientID == 'truck':
            truck.append(client)
            thread = threading.Thread(target = handle_truck, args = (client, address))
            thread.start()
        elif clientID == 'admin':
            admin.append(client)
            thread = threading.Thread(target = handle_admin, args = (client, address))
            thread.start()
        elif clientID == 'tcan':
            print('[NEW TRASHCAN CONNECTED]')
            tcans.append(client)
            thread = threading.Thread(target = handle_tcan, args = (client, address))
            thread.start()

start()


# server.listen()#this socket is going to be listening for connections to be established

# clients = []#list of clients that will be connected to the server
# nicknames = []#list of nicknames for each client connected to the server

# def broadcast(message):
#     #for each client connected to the server in the list of clients, it will receive a message
#     for client in clients:
#         client.send(message)

# def handle(client):
#     while True:
#         try:
#             #the idea is that the server is going to be "listening" to the clients, if they send a message the server is going to pass this message
#             #to the other client. In this case there will be only one client, but in a situation where more than one client exists, I think the solu-
#             #tion would be to put the address of the client that shall receive that message, but it actually will depend on the specifics of how the
#             #system will work, that is still to be seen.
#             message = client.recv(1024)
#             broadcast(message)

#         except:
#             #is the client doesn't respond(as in there is an error in the connection), then the falty client is removed from the list of clients, and 
#             #it's connection is terminated
#             index = clients.index(client)
#             clients.remove(client)
#             client.close()
#             nickname = nicknames[index]
#             nicknames.remove(nickname)
#             break 

# #this function keeps "listening" to connection requests of clients to the server, and if it finds one of those requests it will accept it and receive
# #the client and the address of the client attempting the connection, and store it in the list of clients
# def receive():
#     while True:
#         client, address = server.accept()
#         print(f"Connected with {str(address)}")

#         client.send('NICK'.encode('ascii'))#send the message 'NICK' to the client, so he understands that he can input the client nickname
#         nickname = client.recv(1024).decode('ascii')
#         nicknames.append(nickname)
#         clients.append(client)
        
#         print(f"nickname of the client is {nickname}")
#         broadcast(f"{nickname} just joined the conneciton".encode('ascii'))
#         client.send("connected to the server".encode('ascii'))#sends a message to the connected client to indicate that it is connected

#         #after the client is accepted and the connection is established then we start the thread
#         #for this client
#         thread = threading.Thread(target = handle, args=(client,))
#         thread.start()

# print('server is listening...')
# receive()