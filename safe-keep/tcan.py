import socket
import threading
import time

##Trashcan atributes##
constCapacity = 600
currentLoad = 0
##

host = '127.0.0.1'#localhost 
port = 55555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#this creates an internet socket with the tcp protocol
client.connect((host, port))#connecting to the server binded to this endpoint
client.send('tcan'.encode('utf-8'))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')#this is the client receiving messages from the server, the server, to send messages, uses a client
            if message == 'dump':
                currentLoad = 0
            elif message == 'status':
                client.send(currentLoad.encode('utf-8'))
            else: print(message.decode('utf-8'))
        except:
            print('An error has ocurred!')
            client.close()
            break

#it constantly asks the user how much trash he wants to add, if the quantity overloades the total capacity, a message appears saying it is already filled
def user_input():
    trashUnit = input("[HOW MUCH TRASH DO YOU WANT TO THROW IN THE TRASHCAN?:]\n")
    if type(trashUnit) != int:
        while not type(trashUnit) == int:
            trashUnit = input("[HOW MUCH TRASH DO YOU WANT TO THROW IN THE TRASHCAN?:]\n")
        aux = currentLoad + trashUnit
        if aux >= constCapacity:
            print("[TOTAL CAPACITY OF THE TRASHCAN HAS BEEN REACHED]\n")
        else: 
            currentLoad = aux
    else: 
        aux = currentLoad + trashUnit
        if aux >= constCapacity:
            print("[TOTAL CAPACITY OF THE TRASHCAN HAS BEEN REACHED]\n")
        else:
            currentLoad = aux
        

# def write():
#     #when the client runs the user can either write messages and send them, or close the client. As soon as the user writes a message and clicks enter
#     #the message is sent and the suer can prompt a new message
#     message = f'{nickname}: {input("")}'#waiting for messages written by the client
#     client.send(message.encode('ascii'))

receive_thread = threading.Thread(target = receive)
receive_thread.start()

user_input_thread = threading.Thread(target = user_input)
user_input_thread.start()

# write_thread = threading.Thread(target = write)
# write_thread.start()