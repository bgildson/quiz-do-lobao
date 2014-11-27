# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash
from flask.ext.login import current_user
from app import app, db, forms
from app.models import Questao
from app.enums import QuestaoStatus, UsuarioRole
from .__shared__ import login_required


@app.route('/questao')
@login_required()
def questao():
    questoes_nao_revisadas = db.session.query(Questao) \
        .filter_by(status=QuestaoStatus.nao_revisada.value) \
        .filter_by(enviada_por=current_user._id) \
        .order_by(Questao.data_de_envio.desc()) \
        .all()

    questoes_liberadas = db.session.query(Questao) \
        .filter_by(status=QuestaoStatus.liberada.value) \
        .filter_by(enviada_por=current_user._id) \
        .order_by(Questao.data_de_envio.desc()) \
        .all()

    questoes_bloqueadas = db.session.query(Questao) \
        .filter_by(status=QuestaoStatus.bloqueada.value) \
        .filter_by(enviada_por=current_user._id) \
        .order_by(Questao.data_de_envio.desc()) \
        .all()

    return render_template('/questao/listar.html', questoes_nao_revisadas=questoes_nao_revisadas, 
                                                   questoes_liberadas=questoes_liberadas, 
                                                   questoes_bloqueadas=questoes_bloqueadas)


@app.route('/questao/enviar', methods=['GET', 'POST'])
@login_required()
def questao_enviar():
    form = forms.QuestaoForm()

    if form.validate_on_submit():

        questao = Questao(form.enunciado.data, form.alternativa_a.data, form.alternativa_b.data, form.alternativa_c.data,
                          form.alternativa_d.data, form.alternativa_e.data, form.alternativa_correta.data, current_user._id)
        db.session.add(questao)
        db.session.commit()

        flash('Questão enviada com sucesso!')
        return redirect(url_for('questao'))

    return render_template('/questao/enviar.html', form=form)


@app.route('/revisar')
@login_required(UsuarioRole.admin.value)
def questao_revisar():
    questoes_nao_revisadas = db.session.query(Questao) \
        .filter_by(status=QuestaoStatus.nao_revisada.value) \
        .order_by(Questao.data_de_envio.desc()) \
        .all()

    questoes_liberadas = db.session.query(Questao) \
        .filter_by(status=QuestaoStatus.liberada.value) \
        .order_by(Questao.data_de_envio.desc()) \
        .all()

    questoes_bloqueadas = db.session.query(Questao) \
        .filter_by(status=QuestaoStatus.bloqueada.value) \
        .order_by(Questao.data_de_envio.desc()) \
        .all()

    return render_template('/revisao/listar.html', questoes_nao_revisadas=questoes_nao_revisadas, 
                                                   questoes_liberadas=questoes_liberadas, 
                                                   questoes_bloqueadas=questoes_bloqueadas)


@app.route('/revisar/<int:id>', methods=['GET', 'POST'])
@login_required(UsuarioRole.admin.value)
def questao_revisar_id(id):
    form = forms.QuestaoRevisarForm()
    if id:
        questao = db.session.query(Questao).filter_by(_id=id).first()

        if questao:
            if form.validate_on_submit():
                questao.revisar(form, current_user._id)
                db.session.commit()
                flash('Questão %d revisada com sucesso.' % questao._id)
                return redirect(url_for('questao_revisar'))

            # revisar quais campos serao apresentados
            form.init_from_Questao(questao)

            return render_template('/revisao/revisar.html', form=form, questao_id=questao._id)

        flash('A questão solicitada não existe ou não está mais disponível.')

    return redirect(url_for('questao_revisar'))