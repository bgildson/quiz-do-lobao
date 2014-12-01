# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash
from flask.ext.login import current_user
from .. import db, forms
from ..models import Questao
from ..enums import QuestaoStatus, UsuarioRole
from ..util import login_required


questao = Blueprint('questao', __name__, url_prefix='/questao')

@questao.route('/')
@login_required()
def index():
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

    return render_template('/questao/index.html', questoes_nao_revisadas=questoes_nao_revisadas, 
                                                  questoes_liberadas=questoes_liberadas, 
                                                  questoes_bloqueadas=questoes_bloqueadas)


@questao.route('/novo', methods=['GET', 'POST'])
@login_required()
def novo():
    form = forms.QuestaoForm()

    if form.validate_on_submit():

        questao = Questao(form.enunciado.data, form.alternativa_a.data, form.alternativa_b.data, form.alternativa_c.data,
                          form.alternativa_d.data, form.alternativa_e.data, form.alternativa_correta.data, current_user._id)
        db.session.add(questao)
        db.session.commit()

        flash('Questão enviada com sucesso!')
        return redirect(url_for('questao.index'))

    return render_template('/questao/novo.html', form=form)


@questao.route('/revisar')
@login_required(UsuarioRole.admin.value)
def revisar():
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

    return render_template('questao/revisar.html', questoes_nao_revisadas=questoes_nao_revisadas, 
                                                   questoes_liberadas=questoes_liberadas, 
                                                   questoes_bloqueadas=questoes_bloqueadas)


@questao.route('/revisar/<int:id>', methods=['GET', 'POST'])
@login_required(UsuarioRole.admin.value)
def revisar_id(id):
    form = forms.QuestaoRevisarForm()
    if id:
        questao = db.session.query(Questao).filter_by(_id=id).first()

        if questao:
            if form.validate_on_submit():
                questao.revisar(form, current_user._id)
                db.session.commit()
                flash('Questão %d revisada com sucesso.' % questao._id)
                return redirect(url_for('questao.revisar'))

            # revisar quais campos serao apresentados
            form.init_from_Questao(questao)

            return render_template('questao/revisar_x.html', form=form, questao_id=questao._id)

        flash('A questão solicitada não existe ou não está mais disponível.')

    return redirect(url_for('questao.revisar'))