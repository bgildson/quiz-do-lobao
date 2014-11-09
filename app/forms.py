# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import Required

class CadastroUsuario(Form):
	usuario = TextField('usuario', validators=[Required('O campo "Usuário" é obrigatório.')])
	email = PasswordField('email')
	senha = TextField('senha', validators=[Required('O campo "Senha" é obrigatório.')])
	confirma_senha = TextField('confirma_senha', validators=[Required('O campo "Confirmação de Senha" é obrigatório.')])