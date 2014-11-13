# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask.ext.login import LoginManager, current_user, login_user, logout_user, login_required
from app import app, db, forms
from app.models import Usuario, Questao, Alternativa
from simplejson import dumps
import hashlib


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
	return render_template('/questao/listar.html', questoes=questoes)
	#dumps(questoes)
	#return jsonify(dumps(questoes))

@app.route('/questao/novo', methods=['GET', 'POST'])
@login_required
def questao_novo():
	form = forms.QuestaoForm()
	
	if form.validate_on_submit():
		
		questao = Questao(form.enunciado.data, 'b') #ajustar alternativa correta
		db.session.add(questao)
		db.session.commit()
		
		alternativa_a = Alternativa(form.alternativa_a.data, questao)
		alternativa_b = Alternativa(form.alternativa_b.data, questao)
		alternativa_c = Alternativa(form.alternativa_c.data, questao)
		alternativa_d = Alternativa(form.alternativa_d.data, questao)
		alternativa_e = Alternativa(form.alternativa_e.data, questao)
		
		db.session.add(alternativa_a)
		db.session.add(alternativa_b)
		db.session.add(alternativa_c)
		db.session.add(alternativa_d)
		db.session.add(alternativa_e)
		db.session.commit()

		#flash('Questão cadastrada com sucesso!')
		return redirect( url_for('questao'))
		
	return render_template('/questao/novo.html', form=form)

@app.route('/questao/editar/<int:id>')
@login_required
def questao_editar(id):
	form = forms.QuestaoForm()

	if id:
		questao = db.session.query(Questao).filter_by(_id=id).first()
		if questao:
			form.init_questao(questao)
		else:
			flash('Nenhum registro encontrado para a solicitação.')

	return render_template('/questao/editar.html', form=form, _id=questao._id)

@app.route('/questao/editar/<int:id>', methods=['POST'])
@login_required
def questao_salvar(id):
	form = forms.QuestaoForm()

	if id:
		questao = db.session.query(Questao).filter_by(_id=id).first()
		if form.validate_on_submit():
			print(dir(questao))
			db.session.update(questao)
			db.session.commit()
			return redirect( url_for('questao') )
		else:
			if questao:
				form.init_questao(questao)
		
		return redirect( url_for('questao') )

	return render_template('/questao/editar.html', form=form, _id=questao._id)