import time
import os
import threading
import json
from unicodedata import numeric
import requests
from array import array

#The idea fo the admin is to have an input interface. The functionalities will be:
#The admin can input a number, this number will be the number of trashcans to retreieve from the sectors. The sectors will return
#from the list of all trahcans the most critic ones to amount to the input number.
#
#Once the admin has the list of trashcans on his interface he can select one of the numbers on the list, and it will show the admin
#more information regarding that specific trashcan

def execute_interface():
    while True:
        os.system('cls||clear')
        numberOfTcans = input("[INPUT THE NUMBER OF TRASHCANS YOU WANT TO TRACK:]\n")
        #manda o request para pegar a lista de lixeiras críticas
        payload = {'number': f'{numberOfTcans}'}
        response = requests.get(f"http://127.0.0.1:5000/list-tcans?number={numberOfTcans}")
        aux = response.content.decode()
        aux = aux.split('|')
        tcanList = []
        for i in aux:
            tcanList.append(json.loads(i))
        while True: #aqui eu coloquei um while true imaginando a seguinte lógica: ao mostrar a lista de lixeiras o admin pode selecionar uma lixeira específica
                    #para mostrar mais dados, só que quando ele sair da tela de uma lixeira específica para não atualizar a lista e ele perder a que já tinha,
                    #caso ele queira por exemplo olhar os dados de outra lixeira da lista, ele fica em um outro loop de mostra a lista e escolhe específica.
                    #se ele colocar 'r' para voltar para a tela de pedir um número de lixeiras, o loop é quebrado e ele volta para o loop inicial da interface.
            os.system('cls||clear')
            print(f'####################################\n')
            for i in tcanList:
                print(f'ID: {i["id"]}, Setor: {i["setor"]}\n')
            print(f'####################################\n')
            #printa a lista
            tcanMoreInfo = input("[YOU CAN SELECT ONE TRASHCAN TO SEE IT'S SPECIFIC DETAILS, OR PRESS 'R' TO GO BACK TO THE INITIAL SCREEN]")
            if tcanMoreInfo != 'r':
                os.system('cls||clear')
                print(tcanList[int(tcanMoreInfo)])
                #print só a lixeira selecionada com mais informações
                input("[PRESS ANY KEY TO RETURN TO THE PREVIOUS SCREEN]")
            if tcanMoreInfo == 'r': break


execute_interface()
