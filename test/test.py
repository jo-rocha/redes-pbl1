f = open('test//test.txt', 'r')
#quero colocar uma lixeira id:2, cl:0 no setor 3 existente
#uma lixeira id:1, cl-0 no setor 1 inexistente
rall = f.read()
rall = rall.replace('\n', '')

sID = 3
sID2 = 1
auxStr1 = f's{sID}'
auxStr2 = f's{sID2}'
#construção das strings que vão ser inseridas
id_tcan = 2
auxId = f'id-{id_tcan}'
id_tcan2 = 1
auxId2 = f'id-{id_tcan2}'
cl_tcan = 0
auxCl = f'cl-{cl_tcan}'
cl_tcan2 = 0
auxCl2 = f'cl-{cl_tcan2}'
#


if auxStr1 in rall:
    index = rall.find(auxStr1)
    for index in len(rall):
        if rall[index] == '.':
            newstring = f';'
            rall = rall[:index] + 


rall = rall.replace('\n', '')
print(rall)
