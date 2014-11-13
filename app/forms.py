# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, TextAreaField, RadioField, BooleanField, DateField
from wtforms.validators import Required, Length, EqualTo, Email
from werkzeug.datastructures import MultiDict
from flask.ext.wtf import form

class UsuarioRegistroForm(Form):
	usuario = TextField('Usuário', validators=[Required('O campo "Usuário" é obrigatório.'), Length(max=20, message='O nome do usuário deve conter no máximo 20 caracteres')])
	email = TextField('E-mail', validators=[Required('O campo "E-mail" é obrigatório.'), Email('E-mail informado é inválido')])
	senha = PasswordField('Senha', validators=[Required('O campo "Senha" é obrigatório.')])
	confirma_senha = PasswordField('Confirmação de Senha', validators=[Required('O campo "Confirmação de Senha" é obrigatório.'), EqualTo('senha', 'Preencha os campos de senha corretamente.')])

class UsuarioLoginForm(Form):
	usuario = TextField('Usuário', validators=[Required('O campo "Usuário" é obrigatório.')])
	senha = PasswordField('Senha', validators=[Required('O campo "Senha" é obrigatório.')])

class QuestaoForm(Form):
	enunciado = TextAreaField('Enunciado', validators=[Required('O campo "Enunciado" é obrigatório.')])
	alternativa_a = TextField('Alternativa A', validators=[Required('O campo "Alternativa A" é obrigatório.')])
	alternativa_b = TextField('Alternativa B', validators=[Required('O campo "Alternativa B" é obrigatório.')])
	alternativa_c = TextField('Alternativa C', validators=[Required('O campo "Alternativa C" é obrigatório.')])
	alternativa_d = TextField('Alternativa D', validators=[Required('O campo "Alternativa D" é obrigatório.')])
	alternativa_e = TextField('Alternativa E', validators=[Required('O campo "Alternativa E" é obrigatório.')])
	alternativa_correta = RadioField('Alternativa Correta', default='a', choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E')], validators=[Required('Escolha uma das opções disponibilizadas como resposta.')])
	ativa = BooleanField('Ativa')
	cadastrada_por = TextField('Cadastrada por')
	data_cadastro = DateField('Data de Cadastro')

	def init_questao(self, questao):
		self.enunciado.data = questao.enunciado
		self.alternativa_a.data = questao.alternativas[0].descricao
		self.alternativa_b.data = questao.alternativas[1].descricao
		self.alternativa_c.data = questao.alternativas[2].descricao
		self.alternativa_d.data = questao.alternativas[3].descricao
		self.alternativa_e.data = questao.alternativas[4].descricao
		print(dir(self.alternativa_correta))
		self.alternativa_correta.data = questao.alternativa_correta
		print(questao.alternativa_correta)
		#self.alternativa_correta.populate_obj([ x.descricao for x in ['a', 'b', 'c', 'd', 'e'] if x == questao.alternativa_correta: ]) = questao.alternativa_correta