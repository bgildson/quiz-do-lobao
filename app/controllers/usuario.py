# -*- coding: utf-8 -*-
import hashlib
from flask import render_template, redirect, url_for, flash
from flask.ext.login import current_user, login_user, logout_user
from sqlalchemy.sql.expression import func
from app import app, db, forms
from app.enums import UsuarioRole
from app.models import Usuario
from .__shared__ import login_required


@app.route('/login', methods=['GET', 'POST'])
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
        return redirect(url_for('home'))

    return render_template('usuario/login.html', form=form)


@app.route('/registro', methods=['GET', 'POST'])
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
        return redirect(url_for('home'))

    return render_template('usuario/registro.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/usuario')
@login_required(UsuarioRole.admin.value)
def usuario():
    usuarios = db.session.query(Usuario).order_by(func.random()).all() #.limit(5) -depois adicionar filtro e colocar limit de usuario que devem aparecer
    return render_template('usuario/listar.html', usuarios=usuarios)


@app.route('/usuario/editar/<string:nome_usuario>', methods=['GET', 'POST'])
@login_required(UsuarioRole.admin.value)
def usuario_editar_admin(nome_usuario):
    usuario = db.session.query(Usuario) \
        .filter(func.lower(Usuario.usuario)==nome_usuario.lower()) \
        .first()
    if usuario:
        form = forms.UsuarioEditarAdmin()
        if form.validate_on_submit():
            usuario.editar_admin(form)
            db.session.commit()
            flash('Usuário \'%s\' editado com sucesso!' % usuario.usuario)
            return redirect(url_for('usuario'))
        form.init_from_Usuario(usuario)
        return render_template('usuario/editar_admin.html', form=form)
    flash('Usuário "%s" não encontrado!' % nome_usuario)
    return redirect(url_for('usuario'))
