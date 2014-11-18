# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app import db
from app.enums import StatusQuestao, RetornoResposta
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

	def to_dict(self):
		return {'id': self._id,
				'usuario': self.usuario}

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
	alternativa_a = db.Column(db.String)
	alternativa_b = db.Column(db.String)
	alternativa_c = db.Column(db.String)
	alternativa_d = db.Column(db.String)
	alternativa_e = db.Column(db.String)
	status = db.Column(db.Integer)
	alternativa_correta = db.Column(db.String(1))
	enviada_por = db.Column(db.Integer, ForeignKey('usuarios._id'), nullable=False)
	revisada_por = db.Column(db.Integer, ForeignKey('usuarios._id'))
	observacoes = db.Column(db.String(100))
	partidas = relationship('Partida')

	def __init__(self, enunciado, alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_e, alternativa_correta, usuario_id):
		self.enunciado = enunciado
		self.alternativa_a = alternativa_a
		self.alternativa_b = alternativa_b
		self.alternativa_c = alternativa_c
		self.alternativa_d = alternativa_d
		self.alternativa_e = alternativa_e
		self.status = False
		self.alternativa_correta = alternativa_correta.lower()
		self.enviada_por = usuario_id

	# nem todos os campos devem ser colocados na criacao do dicionario
	def to_dict(self):
		return {'id': self._id,
				'enunciado': self.enunciado,
				'alternativa_a': self.alternativa_a,
				'alternativa_b': self.alternativa_b,
				'alternativa_c': self.alternativa_c,
				'alternativa_d': self.alternativa_d,
				'alternativa_e': self.alternativa_e,
				'enviada_por': self.enviada_por_usuario(),
				'revisada_por': self.revisada_por}

	def init_from_QuestaoForm(self, form):
		self.enunciado = form.enunciado.data
		self.alternativa_a = form.alternativa_a.data
		self.alternativa_b = form.alternativa_b.data
		self.alternativa_c = form.alternativa_c.data
		self.alternativa_d = form.alternativa_d.data
		self.alternativa_e = form.alternativa_e.data
		self.status = form.status.data
		self.alternativa_correta = form.alternativa_correta.data.lower()

	def revisar(self, form):
		self.revisada_por = form.revisada_por.data
		self.observacoes = form.observacoes.data

	def enviada_por_usuario(self):
		return db.session.query(Usuario).filter_by(_id=self.enviada_por).first().usuario or ''

class Partida(db.Model):
	__tablename__ = 'partidas'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	usuario_id = db.Column(db.Integer, ForeignKey('usuarios._id'), nullable=False)
	questao_atual = db.Column(db.Integer, ForeignKey('cad_questoes._id'), nullable=False)
	rodada = db.Column(db.Integer)
	cartas = db.Column(db.Integer)
	pular = db.Column(db.Integer)
	finalizada = db.Column(db.Boolean)
	respostas = relationship('PartidaResposta')

	def __init__(self, usuario_id, questao_id):
		self.usuario_id = usuario_id
		self.questao_atual = questao_id
		self.rodada = 1
		self.cartas = 1
		self.pular = 1
		self.finalizada = False

	def to_dict(self):
		return {'rodada': self.rodada,
				'cartas': self.cartas,
				'pular': self.pular,
				'finalizada': self.finalizada}

class PartidaResposta(db.Model):
	__tablename__ = 'partidas_resposta'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	usuario_id = db.Column(db.Integer, ForeignKey('usuarios._id'), nullable=False)
	questao_id = db.Column(db.Integer, ForeignKey('cad_questoes._id'), nullable=False)
	partida_id = db.Column(db.Integer, ForeignKey('partidas._id'), nullable=False)
	alternativa_respondida = db.Column(db.String(1))
	acertou = db.Column(db.Boolean)

	def __init__(self, usuario_id, questao_id, partida_id, alternativa_respondida, acertou):
		self.usuario_id = usuario_id
		self.questao_id = questao_id
		self.partida_id = partida_id
		self.alternativa_respondida = alternativa_respondida
		self.acertou = acertou