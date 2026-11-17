"""Tela inicial. O conteúdo muda conforme o perfil de quem entrou."""

from datetime import date, datetime, timedelta

from flask import Blueprint, render_template

from models import Agendamento, Animal, AplicacaoVacina, Pagamento, Tutor
from security import exige, usuario_atual, veterinario_da_sessao

bp = Blueprint("painel", __name__)


@bp.route("/")
@exige()
def inicio():
    usuario = usuario_atual()
    inicio_dia = datetime.combine(date.today(), datetime.min.time())
    fim_dia = inicio_dia + timedelta(days=1)

    consulta = Agendamento.query.filter(
        Agendamento.data_hora >= inicio_dia,
        Agendamento.data_hora < fim_dia,
        Agendamento.status != "cancelado",
    )

    # O veterinário enxerga somente a própria agenda.
    vet = veterinario_da_sessao()
    if usuario.perfil == "veterinario" and vet:
        consulta = consulta.filter(Agendamento.veterinario_id == vet.id)

    agenda_hoje = consulta.order_by(Agendamento.data_hora).all()

    cartoes = []
    if usuario.perfil == "veterinario":
        atendidos = [a for a in agenda_hoje if a.status == "atendido"]
        cartoes = [
            ("Consultas hoje", len(agenda_hoje)),
            ("Já atendidas", len(atendidos)),
            ("Aguardando", len(agenda_hoje) - len(atendidos)),
        ]
    else:
        pendentes = Pagamento.query.filter_by(status="pendente").all()
        vencidas = [
            a for a in AplicacaoVacina.query.all() if a.vencida
        ]
        cartoes = [
            ("Consultas hoje", len(agenda_hoje)),
            ("Tutores ativos", Tutor.query.filter_by(ativo=True).count()),
            ("Animais ativos", Animal.query.filter_by(ativo=True).count()),
            ("Pagamentos em aberto", len(pendentes)),
            ("Vacinas vencidas", len(vencidas)),
        ]

    return render_template("painel.html", agenda_hoje=agenda_hoje, cartoes=cartoes)
