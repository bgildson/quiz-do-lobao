# -*- coding: utf-8 -*-
import os
from flask import render_template, send_from_directory
from flask.ext.login import LoginManager, current_user
from sqlalchemy.orm import aliased
from app import app, db
from app.models import Usuario, Partida
from .__shared__ import login_required, get_ranking


lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


@lm.user_loader
def load_user(id):
    return db.session.query(Usuario).filter_by(_id=id).first()


@app.route('/favicon.png')
def favicon():
    return send_from_directory(os.path.join(app.root_path,'images'), 'favicon-quiz-do-lobao_128.png')


@app.route('/')
@login_required()
def home():
    partidas_melhores = get_ranking(5, current_user._id)

    usuario = aliased(Usuario)
    partidas_ultimas = db.session.query(Partida) \
        .join((usuario, current_user._id==Partida.usuario_id)) \
        .order_by(Partida.data_da_partida.desc()) \
        .filter(usuario._id != None) \
        .filter(usuario._id==current_user._id) \
        .filter(Partida.finalizada==True) \
        .limit(5)

    return render_template('index.html', partidas_melhores=partidas_melhores, partidas_ultimas=partidas_ultimas)