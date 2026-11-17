"""Área exclusiva do administrador: usuários e catálogo de vacinas."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from extensions import db
from models import PERFIS, Usuario, Vacina
from security import exige, usuario_atual

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/usuarios")
@exige("administrador")
def usuarios():
    lista = Usuario.query.order_by(Usuario.nome).all()
    return render_template("admin/usuarios.html", usuarios=lista, perfis=PERFIS)


@bp.route("/usuarios/novo", methods=["GET", "POST"])
@bp.route("/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
@exige("administrador")
def form_usuario(usuario_id=None):
    alvo = Usuario.query.get_or_404(usuario_id) if usuario_id else None

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        repetido = Usuario.query.filter_by(email=email).first()
        if repetido and (alvo is None or repetido.id != alvo.id):
            flash("Já existe um usuário com esse e-mail.", "erro")
            return render_template("admin/usuario_form.html", alvo=alvo, perfis=PERFIS)

        if alvo is None:
            alvo = Usuario()
            db.session.add(alvo)
            alvo.definir_senha(request.form.get("senha") or "123456")
        elif request.form.get("senha"):
            alvo.definir_senha(request.form["senha"])

        alvo.nome = request.form["nome"].strip()
        alvo.email = email
        alvo.perfil = request.form["perfil"]
        alvo.ativo = bool(request.form.get("ativo"))
        db.session.commit()
        flash("Usuário salvo.", "ok")
        return redirect(url_for("admin.usuarios"))

    return render_template("admin/usuario_form.html", alvo=alvo, perfis=PERFIS)


@bp.route("/usuarios/<int:usuario_id>/alternar", methods=["POST"])
@exige("administrador")
def alternar_acesso(usuario_id):
    alvo = Usuario.query.get_or_404(usuario_id)
    if alvo.id == usuario_atual().id:
        flash("Você não pode desativar o próprio acesso.", "erro")
        return redirect(url_for("admin.usuarios"))
    alvo.ativo = not alvo.ativo
    db.session.commit()
    flash(
        f"Acesso de {alvo.primeiro_nome} "
        f"{'liberado' if alvo.ativo else 'desativado'}.",
        "ok",
    )
    return redirect(url_for("admin.usuarios"))


@bp.route("/vacinas")
@exige("administrador")
def vacinas():
    lista = Vacina.query.order_by(Vacina.nome).all()
    return render_template("admin/vacinas.html", vacinas=lista)


@bp.route("/vacinas/nova", methods=["GET", "POST"])
@bp.route("/vacinas/<int:vacina_id>/editar", methods=["GET", "POST"])
@exige("administrador")
def form_vacina(vacina_id=None):
    vacina = Vacina.query.get_or_404(vacina_id) if vacina_id else None

    if request.method == "POST":
        if vacina is None:
            vacina = Vacina()
            db.session.add(vacina)
        vacina.nome = request.form["nome"].strip()
        vacina.fabricante = request.form.get("fabricante", "").strip() or None
        vacina.doses_recomendadas = int(request.form.get("doses_recomendadas") or 1)
        vacina.intervalo_dias = int(request.form.get("intervalo_dias") or 365)
        db.session.commit()
        flash("Vacina salva.", "ok")
        return redirect(url_for("admin.vacinas"))

    return render_template("admin/vacina_form.html", vacina=vacina)
