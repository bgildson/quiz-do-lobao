# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager


# cria a aplicacao e informa qual arquivo contem os parametros de configuracao
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')


# cria o objeto de banco de dados da aplicacao
db = SQLAlchemy(app)


from .models import Usuario


lm = LoginManager()
lm.init_app(app)
lm.login_view = 'home.login'


@lm.user_loader
def load_user(id):
    return db.session.query(Usuario).filter_by(_id=id).first()


# registra os Blueprint's
from .views.home import home
from .views.usuario import usuario
from .views.questao import questao
from .views.quiz import quiz


app.register_blueprint(home)
app.register_blueprint(usuario)
app.register_blueprint(questao)
app.register_blueprint(quiz)