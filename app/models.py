from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app import db
import hashlib
import time

class Usuario(db.Model):
	__tablename__ = 'usuarios'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	usuario = db.Column(db.String(20), unique=True)
	senha = db.Column(db.String(32))
	email = db.Column(db.String(70))
	data_cadastro = db.Column(db.Datetime)

	def __init__(self, usuario, senha, email):
		self.usuario = usuario
		self.senha = hashlib.md5(senha.encode('utf-8')).hexdigest()
		self.email = email
		self.data_cadastro = time.strftime('%Y-%m-%d %H:%M:%S')

class Questao(db.Model):
	__tablename__ = 'cad_questoes'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	descricao = db.Column(db.String(255))
	ativo = db.Column(db.Binary)
	alternativas = relationship('Alternativa')

	def __init__(self, descricao):
		self.descricao = descricao
		self.ativo = False

class Alternativa(db.Model):
	__tablename__ = 'cad_alternativas'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	descricao = db.Column(db.String)
	questao_id = db.Column(db.Integer, ForeignKey('cad_questoes._id'))

	def __init__(self, descricao, questao):
		self.descricao = descricao
		self.questao_id = questao._id