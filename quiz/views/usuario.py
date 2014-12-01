# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash
from sqlalchemy.sql.expression import func
from .. import db, forms
from ..enums import UsuarioRole
from ..models import Usuario
from ..util import login_required


usuario = Blueprint('usuario', __name__, url_prefix="/usuario")


@usuario.route('/')
@login_required(UsuarioRole.admin.value)
def index():
    usuarios = db.session.query(Usuario).order_by(func.lower(Usuario.usuario)).all() #.limit(10) - adicionar limite quando adicionar sistema de pesquisa com ajax
    return render_template('usuario/index.html', usuarios=usuarios)


@usuario.route('/editar/<string:nome_usuario>', methods=['GET', 'POST'])
@login_required(UsuarioRole.admin.value)
def editar_como_admin(nome_usuario):
    usuario = db.session.query(Usuario) \
        .filter(func.lower(Usuario.usuario)==nome_usuario.lower()) \
        .first()
    if usuario:
        form = forms.UsuarioEditarAdmin()
        if form.validate_on_submit():
            usuario.editar_admin(form)
            db.session.commit()
            flash('Usuário \'%s\' editado com sucesso!' % usuario.usuario)
            return redirect(url_for('usuario.index'))
        form.init_from_Usuario(usuario)
        return render_template('usuario/editar_como_admin.html', form=form)
    flash('Usuário "%s" não encontrado!' % nome_usuario)
    return redirect(url_for('usuario.index'))