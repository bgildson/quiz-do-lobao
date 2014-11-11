from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# cria a aplicacao e informa qual arquivo contem os parametros de configuracao
app = Flask(__name__)
app.config.from_object('config')

# cria o objeto de banco de dados da aplicacao
db = SQLAlchemy(app)

# carrega os modelos
from app.models import *

# cria o banco de dados baseado nos modelos
db.create_all()

# carrega as toras da aplicacao
from app import views