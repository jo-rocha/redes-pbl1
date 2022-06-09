# Comandos para startar a api
# Na primeira vez que for rodar o arquivo
# $env:FLASK_ENV = "development"
# $env:FLASK_APP = "api"
# 
# flask run
from flask import Flask
from flask import request
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs

app = Flask(__name__)
arquivo = open("listOfTcans.txt", "r")


@app.route('/')
def hello_world():
    """Print 'Hello, world!' as the response body."""
    return 'Hello, world!'

@app.route('/list-tcans')
def list_tcans():
    global arquivo
    # number_lixeiras = json.loads(request.data)['qtd']
    args = request.args
    number_lixeiras = args.get('number')
    tcans = arquivo.readlines()
    # tcans = []
    tcans_temp = list()
    
    index = 0
    for tcan in tcans:
        tcans_temp.append(tcan)
        
        if(index == (number_lixeiras-1)):
            break

        index = index + 1 
    
    return str(tcans_temp) 


@app.route('/get-sectores')
def get_sectores():
    # Retornar setores cadastrados no sistema
    pass

@app.route('/get-tcans')
def get_tcans():
    # Retonar as lixeiras cadastradas no sistema
    pass

@app.route('/get-tcan')
def get_tcan():
    # Retonar as lixeiras cadastradas no sistema
    pass