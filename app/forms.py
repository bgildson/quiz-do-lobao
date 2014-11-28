# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, TextAreaField, RadioField, BooleanField, DateField, SelectField, Label
from wtforms.validators import Required, Length, EqualTo, Email
from werkzeug.datastructures import MultiDict
from flask.ext.wtf import form
from app.enums import UsuarioRole


class UsuarioRegistroForm(Form):
	usuario = TextField('Usuário', validators=[Required('Campo obrigatório.'), Length(max=20, message='O nome do usuário deve conter no máximo 20 caracteres')])
	email = TextField('E-mail', validators=[Required('Campo obrigatório.'), Email('E-mail informado é inválido')])
	senha = PasswordField('Senha', validators=[Required('Campo obrigatório.')])
	confirma_senha = PasswordField('Confirmação de Senha', validators=[Required('Campo obrigatório.'), EqualTo('senha', 'Preencha os campos de senha corretamente.')])


class UsuarioLoginForm(Form):
	usuario = TextField('Usuário', validators=[Required('Campo obrigatório.')])
	senha = PasswordField('Senha', validators=[Required('Campo obrigatório.')])


class QuestaoForm(Form):
	enunciado = TextAreaField('Enunciado', validators=[Required('Campo obrigatório')])
	alternativa_a = TextField('Alternativa A', validators=[Required('Campo obrigatório')])
	alternativa_b = TextField('Alternativa B', validators=[Required('Campo obrigatório')])
	alternativa_c = TextField('Alternativa C', validators=[Required('Campo obrigatório')])
	alternativa_d = TextField('Alternativa D', validators=[Required('Campo obrigatório')])
	alternativa_e = TextField('Alternativa E', validators=[Required('Campo obrigatório')])
	alternativa_correta = RadioField('Alternativa Correta', default='a', choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E')], validators=[Required('Escolha uma das opções disponibilizadas como resposta.')])
	
	def init_from_Questao(self, questao):
		self.enunciado.data = questao.enunciado
		self.alternativa_a.data = questao.alternativa_a
		self.alternativa_b.data = questao.alternativa_b
		self.alternativa_c.data = questao.alternativa_c
		self.alternativa_d.data = questao.alternativa_d
		self.alternativa_e.data = questao.alternativa_e
		self.alternativa_correta.data = questao.alternativa_correta


class QuestaoRevisarForm(Form):
	enunciado = Label('Enunciado', '')
	alternativa_a = Label('Alternativa A', '')
	alternativa_b = Label('Alternativa B', '')
	alternativa_c = Label('Alternativa C', '')
	alternativa_d = Label('Alternativa D', '')
	alternativa_e = Label('Alternativa E', '')
	alternativa_correta = RadioField('Alternativa Correta', default='a', choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E')], validators=[Required('Escolha uma das opções disponibilizadas como resposta.')])
	data_de_envio = Label('Data de Envio', '')
	enviada_por = Label('Enviada por', '')
	revisada_por = Label('Revisada por', '')
	status = SelectField('Status', choices=[('0', 'Não Revisada'), ('1', 'Liberada'), ('2', 'Bloqueada')], default='1')
	observacoes = TextAreaField('Observações')

	def init_from_Questao(self, questao):
		self.enunciado = questao.enunciado
		self.alternativa_a = questao.alternativa_a
		self.alternativa_b = questao.alternativa_b
		self.alternativa_c = questao.alternativa_c
		self.alternativa_d = questao.alternativa_d
		self.alternativa_e = questao.alternativa_e
		self.alternativa_correta.data = questao.alternativa_correta
		self.data_de_envio = questao.data_de_envio_f1
		self.enviada_por = questao.enviada_por_usuario
		self.revisada_por = questao.revisada_por_usuario or ''
		self.status.data = str(questao.status)
		self.observacoes.data = questao.observacoes

class UsuarioEditarAdmin(Form):
	_id = Label('_id', '')
	usuario = Label('usuario', '')
	email = Label('email', '')
	senha = Label('senha', '')
	data_de_cadastro = Label('data_de_cadastro', '')
	role = SelectField('Status', choices=[(str(x.value), x.name) for x in UsuarioRole], default='1')
	ativo = BooleanField('Ativo?', default=True)
	
	def init_from_Usuario(self, usuario):
		self._id = usuario._id
		self.usuario = usuario.usuario
		self.email = usuario.email
		self.senha = usuario.senha
		self.data_de_cadastro = usuario.data_cadastro
		self.role.data = str(usuario.role)
		self.ativo.data = usuario.ativo