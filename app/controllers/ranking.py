# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash
from app import app
from .__shared__ import login_required, get_ranking


@login_required()
@app.route('/ranking')
def ranking():
    return ranking_x(10)


@login_required()
@app.route('/ranking/<int:max>')
def ranking_x(max):
    partidas = get_ranking(max)

    if partidas:
        return render_template('/ranking/Xmelhores.html', partidas=partidas, max=max)
    flash('Ainda não existem partidas para o ranking.')
    return redirect( url_for('home') )