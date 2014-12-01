# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

# cria a aplicacao e informa qual arquivo contem os parametros de configuracao
app = Flask(__name__)
app.config.from_object('config')

# cria o objeto de banco de dados da aplicacao
db = SQLAlchemy(app)

# carrega os modelos
from .models import *

# cria o banco de dados baseado nos modelos
db.create_all()


lm = LoginManager()
lm.init_app(app)
lm.login_view = 'home.login'

@lm.user_loader
def load_user(id):
    return db.session.query(Usuario).filter_by(_id=id).first()

# carrega as toras da aplicacao
#from app import views
#from . import controllers

# registra os Blueprint's
from .views.home import home
from .views.usuario import usuario
from .views.questao import questao
from .views.quiz import quiz

app.register_blueprint(home)
app.register_blueprint(usuario)
app.register_blueprint(questao)
app.register_blueprint(quiz)