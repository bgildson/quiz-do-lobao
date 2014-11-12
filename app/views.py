# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask.ext.login import LoginManager, current_user, login_user, logout_user, login_required
from app import app, db, forms
from app.models import Usuario, Questao, Alternativa
import hashlib
from simplejson import dumps

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

@lm.user_loader
def load_user(id):
	return db.session.query(Usuario).filter_by(_id=id).first()

@app.route('/')
@login_required
def home():
	return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = forms.UsuarioLoginForm()

	if form.validate_on_submit():
		usuario = db.session.query(Usuario).filter_by(usuario=form.usuario.data.lower(), senha=hashlib.md5(form.senha.data.encode('utf-8')).hexdigest()).first()
		if usuario:
			login_user(usuario)
		else:
			flash('Usuário ou Senha inválidos.', 'login')

	if not current_user.is_anonymous() and current_user.is_authenticated():
		return redirect( url_for('home') )

	return render_template('usuario/login.html', form=form)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
	form = forms.UsuarioRegistroForm()

	if form.validate_on_submit():
		usuario = db.session.query(Usuario).filter_by(usuario=form.usuario.data.lower()).first()
		email = db.session.query(Usuario).filter_by(email=form.email.data.lower()).first()

		if usuario:
			flash('Usuário informado já existe.', 'registro')

		if email:
			flash('E-mail informado já esta sendo utilizado.', 'registro')

		if not (usuario or email):
			usuario = Usuario(form.usuario.data, form.email.data, form.senha.data)
			db.session.add(usuario)
			db.session.commit()
			if usuario:
				login_user(usuario)

	if not current_user.is_anonymous() and current_user.is_authenticated():
		return redirect( url_for('home') )

	return render_template('usuario/registro.html', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect( url_for('login') )


@app.route('/jogar')
@login_required
def jogar():
	usuario = db.session.query(Usuario).filter_by(_id=current_user._id).first()

	return 'ok'

@app.route('/questao')
@login_required
def questao():
	questoes = db.session.query(Questao).all()
	n = len(questoes)
	return dumps(questoes)
	#return jsonify(dumps(questoes))

@app.route('/questao/novo', methods=['GET', 'POST'])
@login_required
def questao_novo():
	form = forms.QuestaoForm()

	if form.validate_on_submit():
		questao = Questao(form.enunciado.data, 'alternativa correta')
		if questao:
			db.session.add(questao)
			db.session.commit()
			flash('Questão cadastrada com sucesso!')
	return render_template('questao/novo.html', form=form)