# -*- coding: utf-8 -*-
import hashlib
import os
from flask import Blueprint, render_template, redirect, flash, url_for, send_from_directory
from flask.ext.login import current_user, logout_user, login_user
from sqlalchemy import func
from sqlalchemy.orm import aliased
from .. import app, db, forms
from ..models import Usuario, Partida
from ..util import get_ranking, login_required


home = Blueprint('home', __name__)

# adiciona uma rota para acesso ao favicon da app
@home.route('/favicon.png')
def favicon():
    return send_from_directory(os.path.join(app.root_path,'static'), 'favicon-quiz-do-lobao_128.png')


@home.route('/')
@login_required()
def index():
    partidas_melhores = get_ranking(5, current_user._id)

    usuario = aliased(Usuario)
    partidas_ultimas = db.session.query(Partida) \
        .join((usuario, current_user._id==Partida.usuario_id)) \
        .order_by(Partida.data_da_partida.desc()) \
        .filter(usuario._id != None) \
        .filter(usuario._id==current_user._id) \
        .filter(Partida.finalizada==True) \
        .limit(5)

    return render_template('home/index.html', partidas_melhores=partidas_melhores, partidas_ultimas=partidas_ultimas)


@home.route('/registro', methods=['GET', 'POST'])
def registro():
    form = forms.UsuarioRegistroForm()

    if form.validate_on_submit():
        usuario = db.session.query(Usuario) \
            .filter(func.lower(Usuario.usuario)==form.usuario.data.lower()) \
            .first()
        email = db.session.query(Usuario) \
            .filter_by(email=form.email.data.lower()) \
            .first()

        if usuario:
            flash('Usuário informado já existe.', 'registro')

        if email:
            flash('E-mail informado já esta sendo utilizado.', 'registro')

        if not (usuario or email):
            usuario = Usuario(
                form.usuario.data, form.email.data, form.senha.data)
            db.session.add(usuario)
            db.session.commit()
            if usuario:
                login_user(usuario)

    if not current_user.is_anonymous() and current_user.is_authenticated():
        return redirect(url_for('home.index'))

    return render_template('home/registro.html', form=form)


@home.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.UsuarioLoginForm()

    if form.validate_on_submit():
        usuario = db.session.query(Usuario) \
            .filter_by(usuario=form.usuario.data.lower(), 
                       senha=hashlib.md5(form.senha.data.encode('utf-8')).hexdigest(), 
                       ativo=True) \
            .first()
        if usuario:
            login_user(usuario)
        else:
            flash('Usuário ou Senha inválidos.', 'login')

    if not current_user.is_anonymous() and current_user.is_authenticated():
        return redirect(url_for('home.index'))

    return render_template('home/login.html', form=form)


@home.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.login'))


# wrap ranking :)
@home.route('/ranking')
@login_required()
def ranking():
    return ranking_x(10)


@home.route('/ranking/<int:quantidade>')
@login_required()
def ranking_x(quantidade):
    partidas = get_ranking(quantidade)
    
    if partidas:
        return render_template('/home/ranking.html', partidas=partidas, quantidade=partidas.count())
    flash('Ainda não existem partidas para o ranking.')
    return redirect( url_for('home') )