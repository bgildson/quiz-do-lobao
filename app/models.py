from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app import db
import hashlib
from datetime import datetime

class Usuario(db.Model):
	__tablename__ = 'usuarios'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	usuario = db.Column(db.String(20), unique=True)
	email = db.Column(db.String, unique=True)
	senha = db.Column(db.String(32))
	data_cadastro = db.Column(db.DateTime)

	def __init__(self, usuario, email, senha):
		self.usuario = usuario.lower()
		self.email = email.lower()
		self.senha = hashlib.md5(senha.encode('utf-8')).hexdigest()
		self.data_cadastro = datetime.now()

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self._id

class Questao(db.Model):
	__tablename__ = 'cad_questoes'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	enunciado = db.Column(db.String(255))
	ativo = db.Column(db.Boolean)
	alternativa_correta_id = db.Column(db.Integer, ForeignKey('cad_alternativas._id'))
	alternativas = relationship('Alternativa')

	def __init__(self, enunciado, alternativa_correta):
		self.enunciado = enunciado
		self.alternativa_correta = alternativa_correta
		self.ativo = False

	def init_from_QuestaoForm(form):
		self.enunciado = form.enunciado.data
		self.ativo = form.ativo.data
		self.alternativa_correta = form.alternativa_correta.data

class Alternativa(db.Model):
	__tablename__ = 'cad_alternativas'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	descricao = db.Column(db.String)
	questao_id = db.Column(db.Integer, ForeignKey('cad_questoes._id'))

	def __init__(self, descricao, questao):
		self.descricao = descricao
		self.questao_id = questao._id