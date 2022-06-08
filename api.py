# Comandos para startar a api
# Na primeira vez que for rodar o arquivo
# $env:FLASK_ENV = "development"
# $env:FLASK_APP = "api"
# 
# flask run
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    """Print 'Hello, world!' as the response body."""
    return 'Hello, world!'

@app.route('/list-tcans')
def list_tcans():
    # Retornar x lixeiras indicadas pelo adm
    pass


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