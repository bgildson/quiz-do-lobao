# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import Required, Length, EqualTo, Email

class UsuarioRegistroForm(Form):
	usuario = TextField('usuario', validators=[Required('O campo "Usuário" é obrigatório.'), Length(max=20, message='O nome do usuário deve conter no máximo 20 caracteres')])
	email = TextField('email', validators=[Required('O campo "E-mail" é obrigatório.'), Email('E-mail informado é inválido')])
	senha = PasswordField('senha', validators=[Required('O campo "Senha" é obrigatório.')])
	confirma_senha = PasswordField('confirma_senha', validators=[Required('O campo "Confirmação de Senha" é obrigatório.'), EqualTo('senha', 'Preencha os campos de senha corretamente.')])

class UsuarioLoginForm(Form):
	usuario = TextField('usuario', validators=[Required('O campo "Usuário" é obrigatório.')])
	senha = PasswordField('senha', validators=[Required('O campo "Senha" é obrigatório.')])