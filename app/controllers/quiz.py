# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask.ext.login import current_user
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import func
from sqlalchemy import and_, or_
from app import app, db, forms
from app.models import Questao, Partida, PartidaResposta
from app.enums import RetornoResposta, PartidasRespostaResultado, QuestaoAlternativaCorreta, QuestaoStatus
from .__shared__ import login_required


def QuestaoAlternativaCorreta_is_valid(resposta):
    return resposta in [x.value for x in QuestaoAlternativaCorreta]


def get_questao(partida_id_atual=0):
    partidas_resposta = aliased(PartidaResposta)
    questao = db.session.query(Questao) \
        .outerjoin((partidas_resposta, and_(partidas_resposta.questao_id==Questao._id,
                                            partidas_resposta.partida_id==partida_id_atual))) \
        .filter(partidas_resposta._id == None) \
        .filter(Questao.enviada_por != current_user._id) \
        .filter(Questao.status == QuestaoStatus.liberada.value) \
        .order_by(func.random()) \
        .first()
    return questao


@app.route('/quiz')
@login_required()
def quiz():
    partida = db.session.query(Partida) \
        .filter_by(usuario_id=current_user._id, finalizada=False) \
        .first()

    if partida:
        return render_template('quiz/quiz.html')

    return redirect(url_for('quiz_inicio'))


@app.route('/quiz/inicio')
@login_required()
def quiz_inicio():
    partida = db.session.query(Partida) \
        .filter_by(usuario_id=current_user._id, finalizada=False) \
        .first()

    return render_template('quiz/inicio.html', continuar=partida)


@app.route('/quiz/novo')
@login_required()
def quiz_novo():
    partida = db.session.query(Partida) \
        .filter_by(usuario_id=current_user._id, finalizada=False) \
        .first()

    if partida:
        partida.finalizada = True
        db.session.commit()

    questao = get_questao()

    if questao:
        partida = Partida(current_user._id, questao._id)
        db.session.add(partida)
        db.session.commit()

        return redirect(url_for('quiz'))

    flash('Não foram encontradas questões para responder, por favor, tente jogar mais tarde.')
    return redirect(url_for('quiz_inicio'))


@app.route('/quiz/rodada', methods=['POST'])
@login_required()
def quiz_rodada():
    partida = db.session.query(Partida) \
        .filter_by(usuario_id=current_user._id, finalizada=False) \
        .first()

    if partida:
        questao = db.session.query(Questao) \
            .filter_by(_id=partida.questao_atual) \
            .first()

        if questao:
            return jsonify(partida=partida.to_dict(), questao=questao.to_dict())

    return redirect(url_for('quiz_inicio'))


@app.route('/quiz/responder', methods=['POST'])
@login_required()
def quiz_responder():
    resposta = request.form['resposta']

    if QuestaoAlternativaCorreta_is_valid(resposta):
        partida = db.session.query(Partida) \
            .filter_by(usuario_id=current_user._id, finalizada=False) \
            .first()

        if partida:
            questao_respondida = db.session.query(Questao) \
                .filter_by(_id=partida.questao_atual) \
                .first()

            acertou = questao_respondida.alternativa_correta == resposta

            resultado = PartidasRespostaResultado.acertou.value if acertou else PartidasRespostaResultado.errou.value


            try:
                partidas_resposta = db.session.query(PartidaResposta) \
                    .filter_by(partida_id=partida._id,
                               questao_id=questao_respondida._id) \
                    .first()
                if partidas_resposta:
                    if partidas_resposta.resultado == PartidasRespostaResultado.cartas.value:
                        partida.cartas -= 1
                    partidas_resposta.alternativa_respondida = resposta
                    partidas_resposta.resultado = resultado
                else:
                    partidas_resposta = PartidaResposta(current_user._id, questao_respondida._id,
                                                        partida._id, resposta, resultado)
                    db.session.add(partidas_resposta)

                status = RetornoResposta.continua.value
                if acertou:
                    partida.acertos += 1
                    partida.questao_atual = get_questao(partida._id)._id
                else:
                    partida.finalizada = True
                    status = RetornoResposta.fim_partida.value

                db.session.commit()
                return jsonify({'status': status})

            except:
                db.session.rollback()
                return jsonify({'status': RetornoResposta.error.value, 'message': 'Ocorreu um erro ao tentar processar sua resposta, por favor, tente mais tarde!'})

        return jsonify({'status': RetornoResposta.error.value, 'message': 'Usuário não tem uma partida aberta!'})

    return jsonify({'status': RetornoResposta.error.value, 'message': 'A resposta enviada é inválida!'})


@app.route('/quiz/pular', methods=['POST'])
def quiz_pular():
    partida = db.session.query(Partida) \
        .filter_by(usuario_id=current_user._id, finalizada=False) \
        .first()
    error_message = ''
    if partida:
        if partida.pular < 1:
            error_message = 'Você não pode mais pular questões.'
        else:
            questao_atual = db.session.query(Questao) \
                .filter_by(_id=partida.questao_atual) \
                .first()

            partida_resposta = db.session.query(PartidaResposta) \
                .filter(and_(PartidaResposta.partida_id==partida._id,
                             PartidaResposta.questao_id==questao_atual._id)) \
                .first()

            if partida_resposta:
                partida.cartas -= 1

            if questao_atual:
                try:
                    partidas_resposta = PartidaResposta(current_user._id, questao_atual._id,
                                                        partida._id, '', PartidasRespostaResultado.pulou.value)
                    db.session.add(partidas_resposta)

                    partida.pular -= 1
                    partida.questao_atual = get_questao(partida._id)._id

                    db.session.commit()
                    return jsonify({'status': RetornoResposta.continua.value})
                except:
                    db.session.rollback()
                    error_message = 'Ocorreu um erro ao tentar processar sua requisição.'
            else:
                error_message = 'A questão da partida atual não foi encontrada, por favor, tente iniciar uma nova partida!'
    else:
        error_message = 'Não existe uma partida em andamento, por favor, tente iniciar uma nova partida!'

    return jsonify({'status': RetornoResposta.error.value, 'message': error_message})


@app.route('/quiz/cartas', methods=['POST'])
def quiz_cartas():
    partida = db.session.query(Partida) \
        .filter_by(usuario_id=current_user._id, finalizada=False) \
        .first()
    error_message = ''
    if partida:
        if partida.cartas < 1:
            error_message = 'Você não pode mais usar as cartas.'
        else:
            questao_atual = db.session.query(Questao) \
                .filter_by(_id=partida.questao_atual) \
                .first()

            if questao_atual:
                try:
                    partidas_resposta = db.session.query(PartidaResposta) \
                        .filter_by(partida_id=partida._id,
                                   questao_id=questao_atual._id) \
                        .first()
                    if not partidas_resposta:
                        partidas_resposta = PartidaResposta(current_user._id, questao_atual._id,
                                                            partida._id, '', PartidasRespostaResultado.cartas.value)
                        db.session.add(partidas_resposta)
                        db.session.commit()

                    return jsonify({'status': RetornoResposta.continua.value, 
                                    'alternativa_correta': questao_atual.alternativa_correta,})
                except:
                    db.session.rollback()
                    error_message = 'Ocorreu um erro ao tentar processar sua requisição, por favor, tente mais tarde!'
            else:
                error_message = 'A questão da partida atual não foi encontrada, por favor, tente iniciar uma nova partida!'
    else:
        error_message = 'Não existe uma partida em andamento, por favor, tente iniciar uma nova partida!'

    return jsonify({'status': RetornoResposta.error.value, 'message': error_message})


def get_quiz_resultado(partida_id):
    pass

@app.route('/quiz/resultado')
@login_required()
def quiz_resultado():
    partida = db.session.query(Partida) \
        .filter(Partida.usuario_id==current_user._id) \
        .order_by(Partida.data_da_partida.desc()) \
        .first()
    posicao_ranking = partida.posicao_ranking
    resultado = {'usuario': current_user.usuario,
                 'posicao_ranking': posicao_ranking,}
    return render_template('/quiz/resultado.html', resultado=resultado)