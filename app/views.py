# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask.ext.login import LoginManager, current_user, login_user, logout_user, login_required
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import aliased
from sqlalchemy import and_
from app import app, db, forms
from app.models import Usuario, Questao, Partida,PartidaResposta
from app.enums import StatusQuestao, RetornoResposta
from simplejson import dumps
import hashlib

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


def get_questao(partida_id_atual=0):
	partidas_resposta = aliased(PartidaResposta)
	questao = db.session.query(Questao) \
		.outerjoin((partidas_resposta, and_(partidas_resposta.questao_id==Questao._id, partidas_resposta.partida_id==partida_id_atual))) \
		.filter(and_(partidas_resposta._id == None)) \
		.filter(Questao.cadastrada_por_id!=current_user._id) \
		.filter(Questao.status==StatusQuestao.liberada.value) \
		.order_by(func.random()) \
		.first()
	return questao

def resposta_is_valid(resposta):
	return resposta in ['a', 'b', 'c', 'd', 'e']

@lm.user_loader
def load_user(id):
	return db.session.query(Usuario).filter_by(_id=id).first()

@app.route('/')
@login_required
def home():
	return render_template('index.html', title='Home')


'''''''''''''''''''''''''''''''''''''''''''''
' USUARIO
'''''''''''''''''''''''''''''''''''''''''''''
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = forms.UsuarioLoginForm()

	if form.validate_on_submit():
		usuario = db.session.query(Usuario).filter_by(usuario=form.usuario.data.lower(), senha=hashlib.md5(form.senha.data.encode('utf-8')).hexdigest()).first()
		if usuario:
			login_user(usuario)
		else:
			flash('Usuário ou Senha inválidos.', 'login')

	if not current_user.is_anonymous() and current_user.is_authenticated():
		return redirect( url_for('home') )

	return render_template('usuario/login.html', form=form)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
	form = forms.UsuarioRegistroForm()

	if form.validate_on_submit():
		usuario = db.session.query(Usuario).filter_by(usuario=form.usuario.data.lower()).first()
		email = db.session.query(Usuario).filter_by(email=form.email.data.lower()).first()

		if usuario:
			flash('Usuário informado já existe.', 'registro')

		if email:
			flash('E-mail informado já esta sendo utilizado.', 'registro')

		if not (usuario or email):
			usuario = Usuario(form.usuario.data, form.email.data, form.senha.data)
			db.session.add(usuario)
			db.session.commit()
			if usuario:
				login_user(usuario)

	if not current_user.is_anonymous() and current_user.is_authenticated():
		return redirect( url_for('home') )

	return render_template('usuario/registro.html', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect( url_for('login') )


'''''''''''''''''''''''''''''''''''''''''''''
' QUESTAO
'''''''''''''''''''''''''''''''''''''''''''''
@app.route('/questao')
@login_required
def questao():
	questoes = db.session.query(Questao) \
		.filter_by(cadastrada_por=current_user._id) \
		.all()
	return render_template('/questao/listar.html', questoes=questoes)

@app.route('/questao/enviar', methods=['GET', 'POST'])
@login_required
def questao_enviar():
	form = forms.QuestaoForm()
	
	if form.validate_on_submit():
		
		questao = Questao(form.enunciado.data, form.alternativa_a.data, form.alternativa_b.data, form.alternativa_c.data, \
			 form.alternativa_d.data, form.alternativa_e.data, form.alternativa_correta.data, current_user._id)
		db.session.add(questao)
		db.session.commit()
		
		flash('Questão enviada com sucesso!')
		return redirect( url_for('questao'))
		
	return render_template('/questao/enviar.html', form=form)

@app.route('/questao/revisar/<int:id>', methods=['GET', 'POST'])
@login_required # apenas para admin
def questao_revisar(id): #antigo questao_editar
	form = forms.QuestaoRevisarForm() # criar QuestaoRevisarForm (ira conter apenas os campos necessarios para um admin revisar)

	if id:
		questao = db.session.query(Questao).filter_by(_id=id).first()
		if questao:
			if form.validate_on_submit():
				questao.revisar(form)
				db.session.commit()
				flash('Questão X revisada com sucesso.')
				return redirect( url_for('questao') )
				
			# revisar quais campos serao apresentados
			form.init_from_Questao(questao)
			
			return render_template('/questao/revisar.html', form=form, _id=questao._id)

		flash('A questão solicitada não existe ou não está mais disponível.')

	return redirect( url_for('questao') )


'''''''''''''''''''''''''''''''''''''''''''''
' QUIZ
'''''''''''''''''''''''''''''''''''''''''''''
@app.route('/quiz/inicio')
@login_required
def quiz_inicio():
	partida = db.session.query(Partida).filter_by(usuario_id=current_user._id, finalizada=False).first()

	return render_template('quiz/inicio.html', continuar=partida)

@app.route('/quiz/novo')
@login_required
def quiz_novo():
	partida = db.session.query(Partida).filter_by(usuario_id=current_user._id, finalizada=False).first()

	# se o usuario ja tem alguma partida em aberto
	if partida:
		partida.finalizada = True
		db.session.commit()

	questao = get_questao()

	if questao:
		partida = Partida(current_user._id, questao._id)
		db.session.add(partida)
		db.session.commit()

		return redirect( url_for('quiz') )

	return 'Não foram encontradas questões para responder.'

@app.route('/quiz')
@login_required
def quiz():
	partida = db.session.query(Partida).filter_by(usuario_id=current_user._id, finalizada=False).first()
	
	if partida:
		return render_template('quiz/quiz.html')
	
	return redirect( url_for('quiz_inicio') )

@app.route('/quiz/rodada', methods=['POST'])
@login_required
def quiz_rodada():
	partida = db.session.query(Partida).filter_by(usuario_id=current_user._id, finalizada=False).first()

	if partida:
		questao = db.session.query(Questao).filter_by(_id=partida.questao_atual).first()

		if questao:
			return jsonify(partida=partida.to_dict(), questao=questao.to_dict())

	return redirect( url_for('quiz_inicio') )

@app.route('/quiz/responder', methods=['GET', 'POST'])
@login_required
def quiz_responder():
	resposta = request.form['resposta']

	if resposta_is_valid(resposta):
		partida = db.session.query(Partida).filter_by(usuario_id=current_user._id, finalizada=False).first()

		if partida:
			questao_respondida = db.session.query(Questao).filter_by(_id=partida.questao_atual).first()

			acertou = questao_respondida.alternativa_correta == resposta

			partidas_resposta = PartidaResposta(current_user._id, questao_respondida._id, partida._id, resposta, acertou)
			db.session.add(partidas_resposta)
			db.session.commit()

			status = RetornoResposta.continua.value
			if acertou:
				partida.rodada = partida.rodada + 1
				partida.questao_atual = get_questao(partida._id)._id
			else:
				partida.finalizada = True
				status = RetornoResposta.fim_partida.value
			
			db.session.commit()
			return jsonify({'status': status})

		return jsonify({'status': RetornoResposta.error.value, 'message': 'Usuário não tem uma partida aberta!'})

	return jsonify({'status': RetornoResposta.error.value, 'message': 'A resposta é inválida!'})






#ajustar ainda ta toda errada
def get_quiz_resultado():
	usuario = aliased(Usuario)
	partidas = db.session.query(Partida) \
				.outerjoin((Partida, usuario)) \
				.order_by('rodada').filter()
	return partidas

@app.route('/quiz/resultado', methods=['GET', 'POST'])
@login_required
def quiz_resultado():
	posicao_ranking = 1 #get_quiz_resultado()
	resultado = {'usuario': current_user.usuario, 'posicao_ranking': posicao_ranking}
	return render_template('/quiz/resultado.html', resultado=resultado)