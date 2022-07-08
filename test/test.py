import json
reserveList = [{'sector':2, 'id':1}, {'sector':1, 'id':2}]
jsonList = json.dumps(reserveList)
print(jsonList)
loadList = json.loads(jsonList)
print(loadList[0]['sector'])