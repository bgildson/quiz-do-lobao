from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app import db

class Usuario(db.Model):
	__tablename__ = 'cad_usuarios'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	usuario = db.Column(db.String(20), unique=True)
	senha = db.Column(db.String)

	def __init__(self, usuario, senha):
		self.usuario = usuario
		self.senha = senha

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