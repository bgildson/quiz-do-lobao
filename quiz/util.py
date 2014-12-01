#from flask.ext.login import current_app, current_user
#from functools import wraps

# -*- coding: utf-8 -*-
import hashlib
import os
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask.ext.login import LoginManager, current_app, current_user, login_user, logout_user
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_, over
from . import app, db, forms
from .models import Usuario, Questao, Partida, PartidaResposta
from .enums import QuestaoStatus, RetornoResposta, PartidasRespostaResultado, QuestaoAlternativaCorreta, UsuarioRole
from functools import wraps

# decorator personalizado para implementar restricoes de acesso nas views
# (open source, te amo - haha)
def login_required(*roles):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):

            if current_app.login_manager._login_disabled:
                return func(*args, **kwargs)

            if not current_user.is_authenticated():
                return current_app.login_manager.unauthorized()

            usuario_role = current_user.get_role()
            if (len(roles) > 0) and (usuario_role not in roles):
                logout_user()
                return current_app.login_manager.unauthorized()
            return func(*args, **kwargs)
        return decorated_view
    return wrapper


def get_ranking(quantos, usuario_id=0):
    usuario = aliased(Usuario)
    partidas = db.session.query(Partida) \
        .join((usuario, usuario._id==Partida.usuario_id)) \
        .order_by(Partida.acertos.desc()) \
        .order_by(usuario.usuario) \
        .filter(usuario._id != None) \
        .filter(Partida.finalizada==True) \
        .filter(or_(usuario._id==usuario_id, usuario_id==0)) \
        .limit(quantos)
    return partidas