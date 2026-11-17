"""Cria o banco vetcare.db e preenche com dados de demonstração.

Rode uma única vez, antes do primeiro 'python app.py':

    python seed.py

Se o banco já existir e tiver dados, o script avisa e não faz nada. Para
recomeçar do zero, apague o arquivo vetcare.db e rode de novo.
"""

from datetime import date, datetime, timedelta

from app import criar_app
from extensions import db
from models import (
    Agendamento,
    Animal,
    AplicacaoVacina,
    Especie,
    ItemReceita,
    Pagamento,
    Prontuario,
    Raca,
    Receita,
    Servico,
    Tutor,
    Usuario,
    Vacina,
    Veterinario,
)

SENHA_PADRAO = "123456"


def criar_usuario(nome, email, perfil):
    usuario = Usuario(nome=nome, email=email, perfil=perfil)
    usuario.definir_senha(SENHA_PADRAO)
    db.session.add(usuario)
    return usuario


def povoar():
    # -------------------------------------------------------------- usuários
    admin = criar_usuario("Marina Duarte", "admin@vetcare.vet", "administrador")
    u_helena = criar_usuario("Helena Prado", "helena@vetcare.vet", "veterinario")
    u_rafael = criar_usuario("Rafael Antunes", "rafael@vetcare.vet", "veterinario")
    recepcao = criar_usuario("Carla Nogueira", "recepcao@vetcare.vet", "recepcao")
    db.session.flush()

    helena = Veterinario(
        usuario_id=u_helena.id,
        crmv="SP-18422",
        especialidade="Clínica de pequenos animais",
        telefone="(11) 98877-1020",
    )
    rafael = Veterinario(
        usuario_id=u_rafael.id,
        crmv="SP-20917",
        especialidade="Dermatologia veterinária",
        telefone="(11) 99120-4477",
    )
    db.session.add_all([helena, rafael])

    # ------------------------------------------------------ espécies e raças
    cao = Especie(nome="Cão")
    gato = Especie(nome="Gato")
    coelho = Especie(nome="Coelho")
    db.session.add_all([cao, gato, coelho])
    db.session.flush()

    racas = [
        Raca(nome="Sem raça definida", especie_id=cao.id),
        Raca(nome="Golden Retriever", especie_id=cao.id),
        Raca(nome="Shih Tzu", especie_id=cao.id),
        Raca(nome="Border Collie", especie_id=cao.id),
        Raca(nome="Sem raça definida", especie_id=gato.id),
        Raca(nome="Siamês", especie_id=gato.id),
        Raca(nome="Persa", especie_id=gato.id),
        Raca(nome="Mini Lop", especie_id=coelho.id),
    ]
    db.session.add_all(racas)
    db.session.flush()

    # --------------------------------------------------------------- tutores
    tutores = [
        Tutor(
            nome="Juliana Marques",
            cpf="312.445.780-11",
            telefone="(11) 97412-3388",
            email="juliana.marques@email.com",
            endereco="Rua das Acácias, 120 — Guarulhos/SP",
        ),
        Tutor(
            nome="Pedro Henrique Lima",
            cpf="408.912.335-02",
            telefone="(11) 96330-7781",
            email="pedro.lima@email.com",
            endereco="Av. Tiradentes, 980 — São Paulo/SP",
        ),
        Tutor(
            nome="Aline Castro",
            cpf="221.067.944-50",
            telefone="(11) 98220-5533",
            email="aline.castro@email.com",
            endereco="Rua Pedro Alvares, 45 — Guarulhos/SP",
        ),
        Tutor(
            nome="Ricardo Tanaka",
            cpf="190.554.221-70",
            telefone="(11) 99655-1142",
            endereco="Rua Jacarandá, 310 — Guarulhos/SP",
        ),
    ]
    db.session.add_all(tutores)
    db.session.flush()

    # --------------------------------------------------------------- animais
    animais = [
        Animal(nome="Thor", tutor_id=tutores[0].id, especie_id=cao.id,
               raca_id=racas[1].id, sexo="Macho",
               data_nascimento=date(2021, 3, 14), peso=31.4, pelagem="Dourada",
               observacoes="Agitado durante a contenção. Tutor relata alergia a frango."),
        Animal(nome="Mel", tutor_id=tutores[0].id, especie_id=gato.id,
               raca_id=racas[4].id, sexo="Fêmea",
               data_nascimento=date(2019, 8, 2), peso=4.1, pelagem="Tricolor"),
        Animal(nome="Bidu", tutor_id=tutores[1].id, especie_id=cao.id,
               raca_id=racas[2].id, sexo="Macho",
               data_nascimento=date(2018, 11, 23), peso=7.8, pelagem="Branca e caramelo"),
        Animal(nome="Nina", tutor_id=tutores[2].id, especie_id=gato.id,
               raca_id=racas[5].id, sexo="Fêmea",
               data_nascimento=date(2022, 5, 9), peso=3.6, pelagem="Seal point"),
        Animal(nome="Simba", tutor_id=tutores[2].id, especie_id=cao.id,
               raca_id=racas[3].id, sexo="Macho",
               data_nascimento=date(2020, 1, 30), peso=18.2, pelagem="Preta e branca"),
        Animal(nome="Pipoca", tutor_id=tutores[3].id, especie_id=coelho.id,
               raca_id=racas[7].id, sexo="Fêmea",
               data_nascimento=date(2023, 7, 17), peso=1.9, pelagem="Cinza"),
    ]
    db.session.add_all(animais)
    db.session.flush()

    # -------------------------------------------------------------- serviços
    servicos = [
        Servico(nome="Consulta clínica", descricao="Atendimento de rotina", preco=180.00),
        Servico(nome="Retorno", descricao="Reavaliação em até 15 dias", preco=0.00),
        Servico(nome="Vacinação", descricao="Aplicação de dose única", preco=95.00),
        Servico(nome="Exame de sangue", descricao="Hemograma completo", preco=140.00),
        Servico(nome="Consulta dermatológica", descricao="Avaliação especializada", preco=230.00),
        Servico(nome="Banho terapêutico", descricao="Com xampu medicamentoso", preco=120.00),
    ]
    db.session.add_all(servicos)

    # --------------------------------------------------------------- vacinas
    vacinas = [
        Vacina(nome="V10 (polivalente canina)", fabricante="Zoetis",
               doses_recomendadas=3, intervalo_dias=365),
        Vacina(nome="Antirrábica", fabricante="MSD",
               doses_recomendadas=1, intervalo_dias=365),
        Vacina(nome="V4 (quádrupla felina)", fabricante="Boehringer",
               doses_recomendadas=2, intervalo_dias=365),
        Vacina(nome="Giárdia", fabricante="Zoetis",
               doses_recomendadas=2, intervalo_dias=365),
    ]
    db.session.add_all(vacinas)
    db.session.flush()

    # ----------------------------------------------------------- agendamentos
    hoje = date.today()

    def em(dias, hora, minuto=0):
        return datetime.combine(hoje + timedelta(days=dias), datetime.min.time()).replace(
            hour=hora, minute=minuto
        )

    agendamentos = [
        Agendamento(animal_id=animais[0].id, veterinario_id=helena.id,
                    criado_por_id=recepcao.id, data_hora=em(0, 9, 0),
                    motivo="Consulta de rotina", status="confirmado"),
        Agendamento(animal_id=animais[3].id, veterinario_id=helena.id,
                    criado_por_id=recepcao.id, data_hora=em(0, 10, 30),
                    motivo="Vômito há dois dias", status="agendado",
                    observacoes="Tutora pediu para avisar por WhatsApp se atrasar."),
        Agendamento(animal_id=animais[2].id, veterinario_id=rafael.id,
                    criado_por_id=recepcao.id, data_hora=em(0, 14, 0),
                    motivo="Coceira intensa no dorso", status="agendado"),
        Agendamento(animal_id=animais[4].id, veterinario_id=rafael.id,
                    criado_por_id=recepcao.id, data_hora=em(2, 11, 0),
                    motivo="Revisão dermatológica", status="agendado"),
        Agendamento(animal_id=animais[1].id, veterinario_id=helena.id,
                    criado_por_id=recepcao.id, data_hora=em(-7, 15, 30),
                    motivo="Apatia e perda de apetite", status="atendido"),
        Agendamento(animal_id=animais[5].id, veterinario_id=helena.id,
                    criado_por_id=admin.id, data_hora=em(-14, 9, 30),
                    motivo="Checape geral", status="atendido"),
        Agendamento(animal_id=animais[2].id, veterinario_id=rafael.id,
                    criado_por_id=recepcao.id, data_hora=em(-21, 16, 0),
                    motivo="Dermatite recorrente", status="atendido"),
    ]
    db.session.add_all(agendamentos)
    db.session.flush()

    # ----------------------------------------------------------- prontuários
    p_mel = Prontuario(
        agendamento_id=agendamentos[4].id,
        animal_id=animais[1].id,
        veterinario_id=helena.id,
        data=agendamentos[4].data_hora,
        peso_registrado=4.1,
        anamnese="Tutora relata que a gata está comendo menos há cinco dias e "
                 "passa o dia escondida embaixo da cama. Sem vômito ou diarreia. "
                 "Mora sozinha, não tem acesso à rua.",
        exame_fisico="Mucosas normocoradas, temperatura 39,1 °C, desidratação leve. "
                     "Dor à palpação abdominal cranial. Escore corporal 4/9.",
        diagnostico="Suspeita de gastrite. Solicitado hemograma para descartar "
                    "doença renal, comum na idade.",
        tratamento="Fluidoterapia subcutânea na clínica. Dieta úmida gastrointestinal "
                   "por sete dias e retorno para avaliar o resultado do exame.",
    )
    p_pipoca = Prontuario(
        agendamento_id=agendamentos[5].id,
        animal_id=animais[5].id,
        veterinario_id=helena.id,
        data=agendamentos[5].data_hora,
        peso_registrado=1.9,
        anamnese="Primeira consulta na clínica. Tutor quer avaliação geral e "
                 "orientação sobre alimentação.",
        exame_fisico="Animal alerta, dentes incisivos sem sobrecrescimento, "
                     "pelagem íntegra, ausência de secreção ocular ou nasal.",
        diagnostico="Animal hígido.",
        tratamento="Orientado aumentar a oferta de feno e reduzir ração peletizada. "
                   "Retorno em seis meses.",
    )
    p_bidu = Prontuario(
        agendamento_id=agendamentos[6].id,
        animal_id=animais[2].id,
        veterinario_id=rafael.id,
        data=agendamentos[6].data_hora,
        peso_registrado=7.8,
        anamnese="Terceiro episódio de coceira no ano, sempre no fim do verão. "
                 "Tutor já tentou xampu comum sem melhora.",
        exame_fisico="Eritema em região inguinal e axilar, alopecia por lambedura "
                     "nas patas dianteiras. Sem ectoparasitas visíveis.",
        diagnostico="Dermatite atópica canina, quadro sazonal.",
        tratamento="Antialérgico por 14 dias, banho terapêutico semanal e "
                   "controle ambiental de ácaros.",
    )
    db.session.add_all([p_mel, p_pipoca, p_bidu])
    db.session.flush()

    # --------------------------------------------------------------- receitas
    r_bidu = Receita(
        prontuario_id=p_bidu.id,
        data=p_bidu.data,
        orientacoes="Dar o comprimido junto com a ração para evitar enjoo. "
                    "Não interromper antes do fim, mesmo que a coceira melhore.",
    )
    r_mel = Receita(
        prontuario_id=p_mel.id,
        data=p_mel.data,
        orientacoes="Oferecer a medicação com a comida úmida. Se houver vômito, "
                    "suspender e ligar para a clínica.",
    )
    db.session.add_all([r_bidu, r_mel])
    db.session.flush()

    db.session.add_all([
        ItemReceita(receita_id=r_bidu.id, medicamento="Oclacitinibe 5,4 mg",
                    dosagem="1 comprimido", via="oral",
                    frequencia="12 em 12 h", duracao="14 dias"),
        ItemReceita(receita_id=r_bidu.id, medicamento="Xampu de clorexidina 2%",
                    dosagem="Aplicação tópica", via="tópica",
                    frequencia="1 vez por semana", duracao="4 semanas"),
        ItemReceita(receita_id=r_mel.id, medicamento="Omeprazol 4 mg",
                    dosagem="1 comprimido", via="oral",
                    frequencia="1 vez ao dia, em jejum", duracao="7 dias"),
    ])

    # -------------------------------------------------------------- vacinação
    db.session.add_all([
        AplicacaoVacina(animal_id=animais[0].id, vacina_id=vacinas[0].id,
                        veterinario_id=helena.id,
                        data_aplicacao=hoje - timedelta(days=200),
                        proxima_dose=hoje + timedelta(days=165),
                        dose=3, lote="V10-4412"),
        AplicacaoVacina(animal_id=animais[0].id, vacina_id=vacinas[1].id,
                        veterinario_id=helena.id,
                        data_aplicacao=hoje - timedelta(days=400),
                        proxima_dose=hoje - timedelta(days=35),
                        dose=1, lote="AR-9981"),
        AplicacaoVacina(animal_id=animais[1].id, vacina_id=vacinas[2].id,
                        veterinario_id=helena.id,
                        data_aplicacao=hoje - timedelta(days=120),
                        proxima_dose=hoje + timedelta(days=245),
                        dose=2, lote="V4-2210"),
        AplicacaoVacina(animal_id=animais[2].id, vacina_id=vacinas[1].id,
                        veterinario_id=rafael.id,
                        data_aplicacao=hoje - timedelta(days=430),
                        proxima_dose=hoje - timedelta(days=65),
                        dose=1, lote="AR-9981"),
        AplicacaoVacina(animal_id=animais[4].id, vacina_id=vacinas[0].id,
                        veterinario_id=rafael.id,
                        data_aplicacao=hoje - timedelta(days=60),
                        proxima_dose=hoje + timedelta(days=305),
                        dose=3, lote="V10-4530"),
    ])

    # ------------------------------------------------------------- pagamentos
    db.session.add_all([
        Pagamento(agendamento_id=agendamentos[4].id, servico_id=servicos[0].id,
                  registrado_por_id=recepcao.id, valor=180.00,
                  forma_pagamento="pix", status="pago",
                  data_vencimento=hoje - timedelta(days=7),
                  data_pagamento=hoje - timedelta(days=7)),
        Pagamento(agendamento_id=agendamentos[4].id, servico_id=servicos[3].id,
                  registrado_por_id=recepcao.id, valor=140.00,
                  forma_pagamento="crédito", status="pago",
                  data_vencimento=hoje - timedelta(days=7),
                  data_pagamento=hoje - timedelta(days=7)),
        Pagamento(agendamento_id=agendamentos[6].id, servico_id=servicos[4].id,
                  registrado_por_id=recepcao.id, valor=230.00,
                  status="pendente", data_vencimento=hoje - timedelta(days=4)),
        Pagamento(agendamento_id=agendamentos[5].id, servico_id=servicos[0].id,
                  registrado_por_id=admin.id, valor=180.00,
                  forma_pagamento="dinheiro", status="pago",
                  data_vencimento=hoje - timedelta(days=14),
                  data_pagamento=hoje - timedelta(days=14)),
        Pagamento(agendamento_id=agendamentos[0].id, servico_id=servicos[0].id,
                  registrado_por_id=recepcao.id, valor=180.00,
                  status="pendente", data_vencimento=hoje),
    ])

    db.session.commit()


def main():
    app = criar_app()
    with app.app_context():
        db.create_all()

        if Usuario.query.first():
            print("O banco já tem dados. Nada foi alterado.")
            print("Para recomeçar, apague o arquivo vetcare.db e rode de novo.")
            return

        povoar()

        print("Banco criado com sucesso.")
        print("\nContas de teste (senha 123456 em todas):")
        print("  admin@vetcare.vet      administrador")
        print("  helena@vetcare.vet     veterinária")
        print("  rafael@vetcare.vet     veterinário")
        print("  recepcao@vetcare.vet   recepção")
        print("\nAgora rode: python app.py")


if __name__ == "__main__":
    main()
