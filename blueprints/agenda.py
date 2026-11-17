"""Agenda de consultas.

O veterinário só enxerga os próprios agendamentos — o filtro é aplicado na
consulta ao banco, então nem a listagem nem o acesso direto pela URL vazam
a agenda de outro profissional.
"""

from datetime import datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from extensions import db
from models import STATUS_AGENDAMENTO, Agendamento, Animal, Veterinario
from security import exige, usuario_atual, veterinario_da_sessao

bp = Blueprint("agenda", __name__)


def _agendamento_visivel(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    usuario = usuario_atual()
    if usuario.perfil == "veterinario":
        vet = usuario.veterinario
        if not vet or agendamento.veterinario_id != vet.id:
            abort(403)
    return agendamento


@bp.route("/agenda")
@exige()
def lista():
    status = request.args.get("status", "")
    dia = request.args.get("dia", "")

    consulta = Agendamento.query
    vet = veterinario_da_sessao()
    if usuario_atual().perfil == "veterinario" and vet:
        consulta = consulta.filter(Agendamento.veterinario_id == vet.id)

    if status:
        consulta = consulta.filter(Agendamento.status == status)
    if dia:
        inicio = datetime.strptime(dia, "%Y-%m-%d")
        consulta = consulta.filter(
            Agendamento.data_hora >= inicio,
            Agendamento.data_hora < inicio + timedelta(days=1),
        )

    agendamentos = consulta.order_by(Agendamento.data_hora.desc()).all()
    return render_template(
        "agenda/lista.html",
        agendamentos=agendamentos,
        status=status,
        dia=dia,
        situacoes=STATUS_AGENDAMENTO,
    )


@bp.route("/agenda/nova", methods=["GET", "POST"])
@bp.route("/agenda/<int:agendamento_id>/editar", methods=["GET", "POST"])
@exige("administrador", "recepcao")
def form(agendamento_id=None):
    agendamento = (
        Agendamento.query.get_or_404(agendamento_id) if agendamento_id else None
    )
    animais = Animal.query.filter_by(ativo=True).order_by(Animal.nome).all()
    veterinarios = Veterinario.query.all()

    if request.method == "POST":
        data_hora = datetime.strptime(request.form["data_hora"], "%Y-%m-%dT%H:%M")
        veterinario_id = int(request.form["veterinario_id"])

        # Não deixa marcar dois atendimentos no mesmo horário para o mesmo vet.
        conflito = Agendamento.query.filter(
            Agendamento.veterinario_id == veterinario_id,
            Agendamento.data_hora == data_hora,
            Agendamento.status != "cancelado",
        ).first()
        if conflito and (agendamento is None or conflito.id != agendamento.id):
            flash("Esse veterinário já tem consulta marcada nesse horário.", "erro")
            return render_template(
                "agenda/form.html",
                agendamento=agendamento,
                animais=animais,
                veterinarios=veterinarios,
                situacoes=STATUS_AGENDAMENTO,
            )

        if agendamento is None:
            agendamento = Agendamento(criado_por_id=usuario_atual().id)
            db.session.add(agendamento)

        agendamento.animal_id = int(request.form["animal_id"])
        agendamento.veterinario_id = veterinario_id
        agendamento.data_hora = data_hora
        agendamento.motivo = request.form["motivo"].strip()
        agendamento.status = request.form.get("status", "agendado")
        agendamento.observacoes = request.form.get("observacoes", "").strip() or None
        db.session.commit()
        flash("Agendamento salvo.", "ok")
        return redirect(url_for("agenda.detalhe", agendamento_id=agendamento.id))

    return render_template(
        "agenda/form.html",
        agendamento=agendamento,
        animais=animais,
        veterinarios=veterinarios,
        situacoes=STATUS_AGENDAMENTO,
    )


@bp.route("/agenda/<int:agendamento_id>")
@exige()
def detalhe(agendamento_id):
    agendamento = _agendamento_visivel(agendamento_id)
    return render_template("agenda/detalhe.html", agendamento=agendamento)


@bp.route("/agenda/<int:agendamento_id>/status/<novo>", methods=["POST"])
@exige()
def mudar_status(agendamento_id, novo):
    if novo not in STATUS_AGENDAMENTO:
        abort(404)
    agendamento = _agendamento_visivel(agendamento_id)
    agendamento.status = novo
    db.session.commit()
    flash(f"Consulta marcada como {novo}.", "ok")
    return redirect(url_for("agenda.detalhe", agendamento_id=agendamento.id))
