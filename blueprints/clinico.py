"""Prontuário, receituário e vacinação.

Nenhuma rota deste arquivo aceita o perfil "recepcao": prontuário é informação
clínica e fica restrito ao veterinário que atendeu e ao administrador.
"""

from datetime import date, datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from extensions import db
from models import (
    Agendamento,
    Animal,
    AplicacaoVacina,
    ItemReceita,
    Prontuario,
    Receita,
    Vacina,
)
from security import exige, pode_atender, pode_ver_prontuario, usuario_atual

bp = Blueprint("clinico", __name__)


def _data(campo, padrao=None):
    texto = request.form.get(campo, "").strip()
    if not texto:
        return padrao
    return datetime.strptime(texto, "%Y-%m-%d").date()


# ------------------------------------------------------------------ prontuário
@bp.route("/prontuarios")
@exige("administrador", "veterinario")
def prontuarios():
    usuario = usuario_atual()
    consulta = Prontuario.query
    if usuario.perfil == "veterinario":
        vet = usuario.veterinario
        if not vet:
            abort(403)
        consulta = consulta.filter(Prontuario.veterinario_id == vet.id)
    lista = consulta.order_by(Prontuario.data.desc()).all()
    return render_template("clinico/prontuarios.html", prontuarios=lista)


@bp.route("/agenda/<int:agendamento_id>/prontuario", methods=["GET", "POST"])
@exige("administrador", "veterinario")
def registrar_prontuario(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    if not pode_atender(agendamento):
        abort(403)
    if agendamento.prontuario:
        return redirect(
            url_for("clinico.ver_prontuario", prontuario_id=agendamento.prontuario.id)
        )

    if request.method == "POST":
        peso = request.form.get("peso_registrado", "").replace(",", ".").strip()
        prontuario = Prontuario(
            agendamento_id=agendamento.id,
            animal_id=agendamento.animal_id,
            veterinario_id=agendamento.veterinario_id,
            peso_registrado=float(peso) if peso else None,
            anamnese=request.form["anamnese"].strip(),
            exame_fisico=request.form.get("exame_fisico", "").strip() or None,
            diagnostico=request.form["diagnostico"].strip(),
            tratamento=request.form.get("tratamento", "").strip() or None,
        )
        db.session.add(prontuario)

        if prontuario.peso_registrado:
            agendamento.animal.peso = prontuario.peso_registrado
        agendamento.status = "atendido"
        db.session.commit()
        flash("Atendimento registrado.", "ok")
        return redirect(url_for("clinico.ver_prontuario", prontuario_id=prontuario.id))

    return render_template("clinico/prontuario_form.html", agendamento=agendamento)


@bp.route("/prontuarios/<int:prontuario_id>")
@exige("administrador", "veterinario")
def ver_prontuario(prontuario_id):
    prontuario = Prontuario.query.get_or_404(prontuario_id)
    if not pode_ver_prontuario(prontuario):
        abort(403)
    return render_template("clinico/prontuario.html", prontuario=prontuario)


# --------------------------------------------------------------------- receita
@bp.route("/prontuarios/<int:prontuario_id>/receita", methods=["GET", "POST"])
@exige("administrador", "veterinario")
def nova_receita(prontuario_id):
    prontuario = Prontuario.query.get_or_404(prontuario_id)
    if not pode_ver_prontuario(prontuario):
        abort(403)

    if request.method == "POST":
        receita = Receita(
            prontuario_id=prontuario.id,
            orientacoes=request.form.get("orientacoes", "").strip() or None,
        )
        db.session.add(receita)
        db.session.flush()

        medicamentos = request.form.getlist("medicamento")
        dosagens = request.form.getlist("dosagem")
        vias = request.form.getlist("via")
        frequencias = request.form.getlist("frequencia")
        duracoes = request.form.getlist("duracao")

        for i, medicamento in enumerate(medicamentos):
            if not medicamento.strip():
                continue
            db.session.add(
                ItemReceita(
                    receita_id=receita.id,
                    medicamento=medicamento.strip(),
                    dosagem=dosagens[i].strip() if i < len(dosagens) else "",
                    via=vias[i].strip() if i < len(vias) else None,
                    frequencia=frequencias[i].strip() if i < len(frequencias) else None,
                    duracao=duracoes[i].strip() if i < len(duracoes) else None,
                )
            )

        if not receita.itens and not any(m.strip() for m in medicamentos):
            db.session.rollback()
            flash("Informe pelo menos um medicamento.", "erro")
            return render_template("clinico/receita_form.html", prontuario=prontuario)

        db.session.commit()
        flash("Receita emitida.", "ok")
        return redirect(url_for("clinico.ver_receita", receita_id=receita.id))

    return render_template("clinico/receita_form.html", prontuario=prontuario)


@bp.route("/receitas/<int:receita_id>")
@exige("administrador", "veterinario")
def ver_receita(receita_id):
    receita = Receita.query.get_or_404(receita_id)
    if not pode_ver_prontuario(receita.prontuario):
        abort(403)
    return render_template("clinico/receita.html", receita=receita)


# -------------------------------------------------------------------- vacinas
@bp.route("/vacinacao")
@exige("administrador", "veterinario", "recepcao")
def vacinacao():
    """A recepção acompanha o calendário de vacinas, mas não o prontuário."""
    aplicacoes = AplicacaoVacina.query.order_by(
        AplicacaoVacina.data_aplicacao.desc()
    ).all()
    return render_template("clinico/vacinacao.html", aplicacoes=aplicacoes)


@bp.route("/vacinacao/nova", methods=["GET", "POST"])
@exige("administrador", "veterinario")
def aplicar_vacina():
    animais = Animal.query.filter_by(ativo=True).order_by(Animal.nome).all()
    vacinas = Vacina.query.order_by(Vacina.nome).all()

    if request.method == "POST":
        vacina = Vacina.query.get_or_404(int(request.form["vacina_id"]))
        aplicada_em = _data("data_aplicacao", date.today())
        proxima = _data("proxima_dose")
        if proxima is None and vacina.intervalo_dias:
            proxima = aplicada_em + timedelta(days=vacina.intervalo_dias)

        usuario = usuario_atual()
        aplicacao = AplicacaoVacina(
            animal_id=int(request.form["animal_id"]),
            vacina_id=vacina.id,
            veterinario_id=usuario.veterinario.id if usuario.veterinario else None,
            data_aplicacao=aplicada_em,
            proxima_dose=proxima,
            dose=int(request.form.get("dose") or 1),
            lote=request.form.get("lote", "").strip() or None,
        )
        db.session.add(aplicacao)
        db.session.commit()
        flash("Vacina registrada na carteira do animal.", "ok")
        return redirect(url_for("clinico.vacinacao"))

    animal_sugerido = request.args.get("animal_id", type=int)
    return render_template(
        "clinico/vacina_form.html",
        animais=animais,
        vacinas=vacinas,
        animal_sugerido=animal_sugerido,
    )
