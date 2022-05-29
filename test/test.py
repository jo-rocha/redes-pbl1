dic = {}
dic['value'] = 2
dic2 = {}
dic2['value'] = 1
dic3 = {}
dic3['value'] = 3

list = []
list.append(dic)
list.append(dic2)
list.append(dic3)

list.sort(key = lambda x: int(x['value']), reverse = True)
print(list)
