"""Entrada e saída do sistema."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import Usuario
from security import abrir_sessao, encerrar_sessao, usuario_atual

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if usuario_atual():
        return redirect(url_for("painel.inicio"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario is None or not usuario.conferir_senha(senha):
            flash("E-mail ou senha não conferem.", "erro")
        elif not usuario.ativo:
            flash("Esse acesso está desativado. Procure o administrador.", "erro")
        else:
            abrir_sessao(usuario)
            destino = request.args.get("proximo") or url_for("painel.inicio")
            return redirect(destino)

    return render_template("login.html")


@bp.route("/sair")
def sair():
    encerrar_sessao()
    flash("Você saiu do sistema.", "ok")
    return redirect(url_for("auth.login"))
