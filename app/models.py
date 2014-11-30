# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey, and_, or_, text
from sqlalchemy.orm import relationship, aliased
from sqlalchemy.sql.expression import func
from app import db
from app.enums import QuestaoStatus, RetornoResposta, PartidasRespostaResultado, UsuarioRole
import hashlib
from datetime import datetime


class Usuario(db.Model):
	__tablename__ = 'usuarios'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	usuario = db.Column(db.String(20), unique=True)
	email = db.Column(db.String, unique=True)
	senha = db.Column(db.String(32))
	data_de_cadastro = db.Column(db.DateTime)
	role = db.Column(db.Integer)
	ativo = db.Column(db.Boolean)

	def __init__(self, usuario, email, senha):
		self.usuario = usuario
		self.email = email.lower()
		self.senha = hashlib.md5(senha.encode('utf-8')).hexdigest()
		self.data_de_cadastro = datetime.now()
		self.role = UsuarioRole.user.value
		self.ativo = True

	@property
	def data_de_cadastro_f0(self):
		return self.data_de_cadastro.strftime('%d/%m/%Y')

	@property
	def data_de_cadastro_f1(self):
		return self.data_de_cadastro.strftime('%d/%m/%Y %H:%M')

	@property
	def ativo_texto(self):
		return 'Ativo' if self.ativo else 'Inativo'

	def editar_admin(self, form):
		self.role = form.role.data
		self.ativo = form.ativo.data

	def to_dict(self):
		return {'id': self._id,
				'usuario': self.usuario,}

	def is_authenticated(self):
		return True

	def is_active(self):
		return self.ativo

	def is_anonymous(self):
		return False

	def is_admin(self):
		return self.role == UsuarioRole.admin.value

	def get_id(self):
		return self._id

	def get_role(self):
		return self.role


class Questao(db.Model):
	__tablename__ = 'cad_questoes'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	enunciado = db.Column(db.String(255))
	alternativa_a = db.Column(db.String)
	alternativa_b = db.Column(db.String)
	alternativa_c = db.Column(db.String)
	alternativa_d = db.Column(db.String)
	alternativa_e = db.Column(db.String)
	alternativa_correta = db.Column(db.String(1))
	status = db.Column(db.Integer)
	data_de_envio = db.Column(db.DateTime)
	enviada_por = db.Column(db.Integer, ForeignKey('usuarios._id'), nullable=False)
	revisada_por = db.Column(db.Integer, ForeignKey('usuarios._id'))
	observacoes = db.Column(db.String(100))
	partidas_resposta = relationship('PartidaResposta')

	def __init__(self, enunciado, alternativa_a, alternativa_b, alternativa_c,
				 alternativa_d, alternativa_e, alternativa_correta, usuario_id):
		self.enunciado = enunciado
		self.alternativa_a = alternativa_a
		self.alternativa_b = alternativa_b
		self.alternativa_c = alternativa_c
		self.alternativa_d = alternativa_d
		self.alternativa_e = alternativa_e
		self.alternativa_correta = alternativa_correta.lower()
		self.status = QuestaoStatus.nao_revisada.value
		self.data_de_envio = datetime.now()
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
				'enviada_por': self.enviada_por_usuario,
				'revisada_por': self.revisada_por_usuario,
				}

	def init_from_QuestaoForm(self, form):
		self.enunciado = form.enunciado.data
		self.alternativa_a = form.alternativa_a.data
		self.alternativa_b = form.alternativa_b.data
		self.alternativa_c = form.alternativa_c.data
		self.alternativa_d = form.alternativa_d.data
		self.alternativa_e = form.alternativa_e.data
		self.alternativa_correta = form.alternativa_correta.data.lower()
		self.status = form.status.data

	def revisar(self, form, revisada_por):
		self.status = form.status.data
		self.revisada_por = revisada_por
		self.observacoes = form.observacoes.data

	@property
	def status_descricao(self):
		if self.status == QuestaoStatus.bloqueada.value:
			return 'Bloqueada'
		elif self.status == QuestaoStatus.liberada.value:
			return 'Liberada'
		return 'Não Revisada'

	@property
	def enviada_por_usuario(self):
		usuario = db.session.query(Usuario) \
			.filter_by(_id=self.enviada_por) \
			.first()
		return usuario.usuario if usuario else ''

	@property
	def revisada_por_usuario(self):
		usuario = db.session.query(Usuario) \
			.filter_by(_id=self.revisada_por) \
			.first()
		return usuario.usuario if usuario else ''

	@property
	def data_de_envio_f0(self):
		return self.data_de_envio.strftime('%d/%m/%Y')

	@property
	def data_de_envio_f1(self):
		return self.data_de_envio.strftime('%d/%m/%Y %H:%M')


class Partida(db.Model):
	__tablename__ = 'partidas'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	usuario_id = db.Column(db.Integer, ForeignKey('usuarios._id'), nullable=False)
	data_da_partida = db.Column(db.DateTime)
	questao_atual = db.Column(db.Integer, ForeignKey('cad_questoes._id'), nullable=False)
	acertos = db.Column(db.Integer)
	cartas = db.Column(db.Integer)
	pular = db.Column(db.Integer)
	finalizada = db.Column(db.Boolean)
	respostas = relationship('PartidaResposta')

	def __init__(self, usuario_id, questao_id):
		self.usuario_id = usuario_id
		self.data_da_partida = datetime.now()
		self.questao_atual = questao_id
		self.acertos = 0
		self.cartas = 1
		self.pular = 3
		self.finalizada = False

	def to_dict(self):
		return {'acertos': self.acertos,
				'cartas': self.cartas,
				'pular': self.pular,
				'finalizada': self.finalizada,
				'data_da_partida': self.data_da_partida,}

	@property
	def posicao_meu_ranking(self):
		posicao = db.session.query(Partida) \
			.filter(Partida.usuario_id==self.usuario_id,
					or_(Partida.acertos>self.acertos, 
						and_(Partida._id<self._id,
							 Partida.acertos==self.acertos))) \
			.count()
		return posicao + 1

	@property
	def posicao_ranking(self):
		usuario = aliased(Usuario)
		posicao = db.session.query(Partida) \
			.join((usuario, usuario._id==Partida.usuario_id)) \
			.filter(or_(Partida.acertos>self.acertos, 
						and_(usuario.usuario<self.usuario,
							 Partida.acertos==self.acertos),
						and_(Partida._id<self._id,
							 Partida.usuario_id==self.usuario_id,
							 Partida.acertos==self.acertos))) \
			.count()
		return posicao + 1

	@property
	def usuario(self):
		usuario = db.session.query(Usuario).filter_by(_id=self.usuario_id).first()
		return usuario.usuario if usuario else ''

	@property
	def data_da_partida_f0(self):
		return self.data_da_partida.strftime('%d/%m/%Y')

	@property
	def data_da_partida_c(self):
		return self.data_da_partida.strftime('%Y-%m-%d %H:%M:%S')

class PartidaResposta(db.Model):
	__tablename__ = 'partidas_resposta'

	_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	usuario_id = db.Column(db.Integer, ForeignKey('usuarios._id'), nullable=False)
	questao_id = db.Column(db.Integer, ForeignKey('cad_questoes._id'), nullable=False)
	partida_id = db.Column(db.Integer, ForeignKey('partidas._id'), nullable=False)
	alternativa_respondida = db.Column(db.String(1))
	resultado = db.Column(db.Integer)
	
	def __init__(self, usuario_id, questao_id, partida_id, alternativa_respondida, resultado=PartidasRespostaResultado.aguardando.value):
		self.usuario_id = usuario_id
		self.questao_id = questao_id
		self.partida_id = partida_id
		self.alternativa_respondida = alternativa_respondida
		self.resultado = resultado