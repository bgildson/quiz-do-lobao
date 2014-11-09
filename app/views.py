from flask import render_template, request, redirect
from app import app
from app import forms

@app.route('/')
def home():
	return 'ok'


@app.route('/usuario/novo', methods=['GET', 'POST'])
def usuario_novo():
	form_novo = forms.CadastroUsuario()
	return render_template('usuario/form_novo.html', form_novo=form_novo)