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
import socket
import threading

FLASK_ENV = "development"
FLASK_APP = "api"
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASK_ENV', silent=True)
app.config.from_envvar('FLASK_APP', silent=True)

@app.route('/list-tcans')
def list_tcans():
    return str("Hello World")
    

@app.route('/dump-tcan')
def dump_tcan():

    args = request.args
    number_lixeiras = int(args.get('number'))
    id_sector = int(args.get('sector'))

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

if __name__ == '__main__':
    app.run(port="8080")
