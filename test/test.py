toReserveList = []
userInput = input("[SELECT WHICH TRASHCANS YOU WANT TO RESERVE. ENTER THE SECTOR ID FOLLOWED BY ',' THEN THE TRASHCAN ID\nTO SEPARATE ONE REQUEST FROM THE OTHER USE ';']\n")
counter = 0
dict = {}
sectorAlreadyExists = False
if '0' not in userInput:
    if ';' in userInput:
        userInput = userInput.split(';')                                
        for i in userInput:
            dict = {}
            if toReserveList:
                i = i.split(',')
                for j in toReserveList:
                    if j['sector'] == i[0]:
                        appendList = j['tcan']
                        print(appendList)
                        appendList.append(i[1])
                        j['tcan'] == appendList
                        sectorAlreadyExists = True
                if sectorAlreadyExists == False:
                    dict['sector'] = i[0]
                    appendList = []
                    appendList.append(i[1])
                    dict['tcan'] = appendList
                    toReserveList.append(dict)
            else:
                i = i.split(',')
                dict['sector'] = i[0]
                appendList = []
                appendList.append(i[1])
                dict['tcan'] = appendList
                toReserveList.append(dict)
    else:
        userInput = userInput.split(',')
        dict['sector'] = userInput[0]
        appendList = []
        appendList.append(userInput[1])
        dict['tcan'] = appendList
        toReserveList.append(dict)
print(toReserveList)