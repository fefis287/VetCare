"""Tabela de serviços e lançamento de pagamentos.

Área da recepção e do administrador. O veterinário não entra aqui.
"""

from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from extensions import db
from models import (
    FORMAS_PAGAMENTO,
    STATUS_PAGAMENTO,
    Agendamento,
    Pagamento,
    Servico,
)
from security import exige, usuario_atual

bp = Blueprint("financeiro", __name__)


def _data(campo):
    texto = request.form.get(campo, "").strip()
    return datetime.strptime(texto, "%Y-%m-%d").date() if texto else None


# ----------------------------------------------------------------- pagamentos
@bp.route("/pagamentos")
@exige("administrador", "recepcao")
def pagamentos():
    status = request.args.get("status", "")
    consulta = Pagamento.query
    if status:
        consulta = consulta.filter(Pagamento.status == status)
    lista = consulta.order_by(Pagamento.id.desc()).all()

    total_pago = sum(p.valor for p in lista if p.status == "pago")
    total_aberto = sum(p.valor for p in lista if p.status == "pendente")

    return render_template(
        "financeiro/pagamentos.html",
        pagamentos=lista,
        status=status,
        situacoes=STATUS_PAGAMENTO,
        total_pago=total_pago,
        total_aberto=total_aberto,
    )


@bp.route("/pagamentos/novo", methods=["GET", "POST"])
@exige("administrador", "recepcao")
def novo_pagamento():
    agendamentos = (
        Agendamento.query.filter(Agendamento.status != "cancelado")
        .order_by(Agendamento.data_hora.desc())
        .limit(80)
        .all()
    )
    servicos = Servico.query.filter_by(ativo=True).order_by(Servico.nome).all()

    if request.method == "POST":
        servico = Servico.query.get_or_404(int(request.form["servico_id"]))
        valor = request.form.get("valor", "").replace(",", ".").strip()
        status = request.form.get("status", "pendente")

        pagamento = Pagamento(
            agendamento_id=int(request.form["agendamento_id"]),
            servico_id=servico.id,
            registrado_por_id=usuario_atual().id,
            valor=float(valor) if valor else servico.preco,
            forma_pagamento=request.form.get("forma_pagamento") or None,
            status=status,
            data_vencimento=_data("data_vencimento"),
            data_pagamento=date.today() if status == "pago" else None,
        )
        db.session.add(pagamento)
        db.session.commit()
        flash("Lançamento registrado.", "ok")
        return redirect(url_for("financeiro.pagamentos"))

    agendamento_sugerido = request.args.get("agendamento_id", type=int)
    return render_template(
        "financeiro/pagamento_form.html",
        agendamentos=agendamentos,
        servicos=servicos,
        formas=FORMAS_PAGAMENTO,
        situacoes=STATUS_PAGAMENTO,
        agendamento_sugerido=agendamento_sugerido,
    )


@bp.route("/pagamentos/<int:pagamento_id>/baixa", methods=["POST"])
@exige("administrador", "recepcao")
def dar_baixa(pagamento_id):
    pagamento = Pagamento.query.get_or_404(pagamento_id)
    pagamento.status = "pago"
    pagamento.data_pagamento = date.today()
    pagamento.forma_pagamento = (
        request.form.get("forma_pagamento") or pagamento.forma_pagamento
    )
    db.session.commit()
    flash("Pagamento baixado.", "ok")
    return redirect(url_for("financeiro.pagamentos"))


# ------------------------------------------------------------------- serviços
@bp.route("/servicos")
@exige("administrador", "recepcao")
def servicos():
    lista = Servico.query.order_by(Servico.nome).all()
    return render_template("financeiro/servicos.html", servicos=lista)


@bp.route("/servicos/novo", methods=["GET", "POST"])
@bp.route("/servicos/<int:servico_id>/editar", methods=["GET", "POST"])
@exige("administrador")
def form_servico(servico_id=None):
    servico = Servico.query.get_or_404(servico_id) if servico_id else None

    if request.method == "POST":
        if servico is None:
            servico = Servico()
            db.session.add(servico)
        servico.nome = request.form["nome"].strip()
        servico.descricao = request.form.get("descricao", "").strip() or None
        servico.preco = float(request.form["preco"].replace(",", "."))
        servico.ativo = bool(request.form.get("ativo"))
        db.session.commit()
        flash("Serviço salvo.", "ok")
        return redirect(url_for("financeiro.servicos"))

    return render_template("financeiro/servico_form.html", servico=servico)
