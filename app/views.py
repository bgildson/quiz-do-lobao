from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import LoginManager, current_user, login_user, logout_user, login_required
from app import app, db, forms
from app.models import Usuario
import hashlib

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'registro_login'

@app.route('/')
@login_required
def home():
	return 'ok'

@app.route('/acesso', methods=['GET', 'POST'])
def registro_login():
	# cria os formularios presentes na pagina
	form_login = forms.UsuarioLoginForm()
	form_registro = forms.UsuarioRegistroForm()

	# verifica se houve uma solicitacao de login
	if form_login.validate_on_submit():
		usuario = db.session.query(Usuario).filter_by(usuario=form_login.usuario_.data.lower(), senha=hashlib.md5(form_login.senha_.data.encode('utf-8')).hexdigest()).first()
		if usuario:
			login_user(usuario)

	# verifica se houve uma solicitacao de registro
	if form_registro.validate_on_submit():
		usuario = db.session.query(Usuario).filter_by(usuario=form_registro.usuario.data.lower()).first()
		email = db.session.query(Usuario).filter_by(email=form_registro.email.data.lower()).first()

		# verifica se ja nao existe algum usuario cadastrado com o mesmo nome ou email informados
		if usuario:
			flash('Usuário informado já existe.')
		elif email:
			flash('E-mail informado já esta sendo utilizado.')
		else:
			usuario = Usuario(form_registro.usuario.data, form_registro.email.data, form_registro.senha.data)
			db.session.add(usuario)
			db.session.commit()
			if usuario:
				login_user(usuario)

	# verifica se ja existe algum usuario autenticado
	if current_user.is_authenticated() and not current_user.is_anonymous():
		return redirect( url_for('home') )

	return render_template('acesso.html', form_registro=form_registro, form_login=form_login)

@app.route('/logout')
def logout():
	logout_user()
	return redirect( url_for('registro_login') )