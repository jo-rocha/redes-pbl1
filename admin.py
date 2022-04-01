import socket
import threading
import constant
import json

clientID = 'admin'

#Connection to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((constant.Host, constant.Port))

def receive():
    #if the message received from the server is 'ID' we send the ID 'truck' if it is any other message from the trashcan we just print it
    while True:
        try:
            message = json.loads(client.recv(1024).decode('ascii'))
            route = message["route"]
            if route == 'get-next-tcan':
                # Retorna a próxima lixeira da lista de lixeiras
                pass
            elif route == 'get-list-tcan':
                # Retorna a lista de lixeiras já ordenadas
                pass
            else:
                print(f'{message}\n\n')
        except:
            print('[ERROR ADMIN!]')
            break


def write():
    #the message will be the input of the user
    while True:
        # message = '{}'.format(input(''))
        request = input('[CHOOSE AN OPERATION]\n1-CHANGE STATUS TRASHCAN\n2-CHANGE CAPACITY TRASHCAN\n3-GET STATUS TRASHCANS\n4-CHANGE ORDER LIST TRASHCANS')
        if request == "1":
            change_status_tcan()
        elif request == "2":
            change_capacity_tcan()
        elif request == "3":
            get_status_tcans()
        elif request == "4":
            change_order_list_tcan()
        else:
            print("CHOOSE VALID OPTION")
        # client.send(message_JSON.encode('ascii'))

# Change status the tcan (blocked or released)
def change_status_tcan():
    print("Mudar status da lixeira")
    pass

# Change the capacity tcan
def change_capacity_tcan():
    print("Mudar capacidade da lixeira")
    pass

#Get status the list of tcans
def get_status_tcans():
    print("Pegar status das lixeiras")
    pass

# Change order the list of tcan
def change_order_list_tcan():
    print("Mudar ordem da lista das lixeiras")
    pass

# Starting threads
receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()