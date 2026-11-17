"""Modelo de dados do VetCare.

São 14 tabelas, agrupadas em quatro blocos:

  Acesso      -> usuarios, veterinarios
  Cadastros   -> tutores, animais, especies, racas
  Clinico     -> agendamentos, prontuarios, receitas, itens_receita,
                 vacinas, aplicacoes_vacina
  Financeiro  -> servicos, pagamentos
"""

from datetime import datetime, date

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

PERFIS = ("administrador", "veterinario", "recepcao")

ROTULO_PERFIL = {
    "administrador": "Administrador",
    "veterinario": "Veterinário",
    "recepcao": "Recepção",
}


# --------------------------------------------------------------------- acesso
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), nullable=False, default="recepcao")
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    veterinario = db.relationship(
        "Veterinario", back_populates="usuario", uselist=False
    )

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def conferir_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def rotulo_perfil(self):
        return ROTULO_PERFIL.get(self.perfil, self.perfil)

    @property
    def primeiro_nome(self):
        return self.nome.split()[0]

    def __repr__(self):
        return f"<Usuario {self.email} ({self.perfil})>"


class Veterinario(db.Model):
    __tablename__ = "veterinarios"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(
        db.Integer, db.ForeignKey("usuarios.id"), nullable=False, unique=True
    )
    crmv = db.Column(db.String(20), nullable=False, unique=True)
    especialidade = db.Column(db.String(80))
    telefone = db.Column(db.String(20))

    usuario = db.relationship("Usuario", back_populates="veterinario")
    agendamentos = db.relationship("Agendamento", back_populates="veterinario")

    @property
    def nome(self):
        return self.usuario.nome

    def __repr__(self):
        return f"<Veterinario {self.crmv}>"


# ------------------------------------------------------------------ cadastros
class Especie(db.Model):
    __tablename__ = "especies"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False, unique=True)

    racas = db.relationship("Raca", back_populates="especie")
    animais = db.relationship("Animal", back_populates="especie")

    def __repr__(self):
        return f"<Especie {self.nome}>"


class Raca(db.Model):
    __tablename__ = "racas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    especie_id = db.Column(db.Integer, db.ForeignKey("especies.id"), nullable=False)

    especie = db.relationship("Especie", back_populates="racas")
    animais = db.relationship("Animal", back_populates="raca")

    def __repr__(self):
        return f"<Raca {self.nome}>"


class Tutor(db.Model):
    __tablename__ = "tutores"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    endereco = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    animais = db.relationship("Animal", back_populates="tutor")

    @property
    def animais_ativos(self):
        return [a for a in self.animais if a.ativo]

    def __repr__(self):
        return f"<Tutor {self.nome}>"


class Animal(db.Model):
    __tablename__ = "animais"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey("tutores.id"), nullable=False)
    especie_id = db.Column(db.Integer, db.ForeignKey("especies.id"), nullable=False)
    raca_id = db.Column(db.Integer, db.ForeignKey("racas.id"))
    sexo = db.Column(db.String(10))
    data_nascimento = db.Column(db.Date)
    peso = db.Column(db.Float)
    pelagem = db.Column(db.String(60))
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    tutor = db.relationship("Tutor", back_populates="animais")
    especie = db.relationship("Especie", back_populates="animais")
    raca = db.relationship("Raca", back_populates="animais")
    agendamentos = db.relationship("Agendamento", back_populates="animal")
    prontuarios = db.relationship("Prontuario", back_populates="animal")
    aplicacoes = db.relationship("AplicacaoVacina", back_populates="animal")

    @property
    def idade(self):
        """Idade em anos e meses, calculada a partir da data de nascimento."""
        if not self.data_nascimento:
            return "não informada"
        hoje = date.today()
        meses = (hoje.year - self.data_nascimento.year) * 12 + (
            hoje.month - self.data_nascimento.month
        )
        if hoje.day < self.data_nascimento.day:
            meses -= 1
        meses = max(meses, 0)
        anos, resto = divmod(meses, 12)
        if anos and resto:
            return f"{anos} a {resto} m"
        if anos:
            return f"{anos} ano(s)"
        return f"{resto} mes(es)"

    def __repr__(self):
        return f"<Animal {self.nome}>"


# -------------------------------------------------------------------- clinico
STATUS_AGENDAMENTO = ("agendado", "confirmado", "atendido", "cancelado")


class Agendamento(db.Model):
    __tablename__ = "agendamentos"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animais.id"), nullable=False)
    veterinario_id = db.Column(
        db.Integer, db.ForeignKey("veterinarios.id"), nullable=False
    )
    criado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    data_hora = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="agendado")
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    animal = db.relationship("Animal", back_populates="agendamentos")
    veterinario = db.relationship("Veterinario", back_populates="agendamentos")
    criado_por = db.relationship("Usuario")
    prontuario = db.relationship(
        "Prontuario", back_populates="agendamento", uselist=False
    )
    pagamentos = db.relationship("Pagamento", back_populates="agendamento")

    @property
    def total_cobrado(self):
        return sum(p.valor for p in self.pagamentos if p.status != "cancelado")

    def __repr__(self):
        return f"<Agendamento {self.id} {self.data_hora:%d/%m %H:%M}>"


class Prontuario(db.Model):
    __tablename__ = "prontuarios"

    id = db.Column(db.Integer, primary_key=True)
    agendamento_id = db.Column(
        db.Integer, db.ForeignKey("agendamentos.id"), nullable=False, unique=True
    )
    animal_id = db.Column(db.Integer, db.ForeignKey("animais.id"), nullable=False)
    veterinario_id = db.Column(
        db.Integer, db.ForeignKey("veterinarios.id"), nullable=False
    )
    data = db.Column(db.DateTime, nullable=False, default=datetime.now)
    peso_registrado = db.Column(db.Float)
    anamnese = db.Column(db.Text, nullable=False)
    exame_fisico = db.Column(db.Text)
    diagnostico = db.Column(db.Text, nullable=False)
    tratamento = db.Column(db.Text)

    agendamento = db.relationship("Agendamento", back_populates="prontuario")
    animal = db.relationship("Animal", back_populates="prontuarios")
    veterinario = db.relationship("Veterinario")
    receitas = db.relationship(
        "Receita", back_populates="prontuario", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Prontuario {self.id}>"


class Receita(db.Model):
    __tablename__ = "receitas"

    id = db.Column(db.Integer, primary_key=True)
    prontuario_id = db.Column(
        db.Integer, db.ForeignKey("prontuarios.id"), nullable=False
    )
    data = db.Column(db.DateTime, nullable=False, default=datetime.now)
    orientacoes = db.Column(db.Text)

    prontuario = db.relationship("Prontuario", back_populates="receitas")
    itens = db.relationship(
        "ItemReceita", back_populates="receita", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Receita {self.id}>"


class ItemReceita(db.Model):
    __tablename__ = "itens_receita"

    id = db.Column(db.Integer, primary_key=True)
    receita_id = db.Column(db.Integer, db.ForeignKey("receitas.id"), nullable=False)
    medicamento = db.Column(db.String(120), nullable=False)
    dosagem = db.Column(db.String(60), nullable=False)
    via = db.Column(db.String(40))
    frequencia = db.Column(db.String(60))
    duracao = db.Column(db.String(60))

    receita = db.relationship("Receita", back_populates="itens")

    def __repr__(self):
        return f"<ItemReceita {self.medicamento}>"


class Vacina(db.Model):
    __tablename__ = "vacinas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False, unique=True)
    fabricante = db.Column(db.String(80))
    doses_recomendadas = db.Column(db.Integer, default=1)
    intervalo_dias = db.Column(db.Integer, default=365)

    aplicacoes = db.relationship("AplicacaoVacina", back_populates="vacina")

    def __repr__(self):
        return f"<Vacina {self.nome}>"


class AplicacaoVacina(db.Model):
    __tablename__ = "aplicacoes_vacina"

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey("animais.id"), nullable=False)
    vacina_id = db.Column(db.Integer, db.ForeignKey("vacinas.id"), nullable=False)
    veterinario_id = db.Column(db.Integer, db.ForeignKey("veterinarios.id"))
    data_aplicacao = db.Column(db.Date, nullable=False, default=date.today)
    proxima_dose = db.Column(db.Date)
    dose = db.Column(db.Integer, default=1)
    lote = db.Column(db.String(40))

    animal = db.relationship("Animal", back_populates="aplicacoes")
    vacina = db.relationship("Vacina", back_populates="aplicacoes")
    veterinario = db.relationship("Veterinario")

    @property
    def vencida(self):
        return bool(self.proxima_dose and self.proxima_dose < date.today())

    def __repr__(self):
        return f"<AplicacaoVacina {self.id}>"


# ----------------------------------------------------------------- financeiro
FORMAS_PAGAMENTO = ("dinheiro", "pix", "débito", "crédito", "convênio")
STATUS_PAGAMENTO = ("pendente", "pago", "cancelado")


class Servico(db.Model):
    __tablename__ = "servicos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, unique=True)
    descricao = db.Column(db.String(200))
    preco = db.Column(db.Float, nullable=False, default=0.0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    pagamentos = db.relationship("Pagamento", back_populates="servico")

    def __repr__(self):
        return f"<Servico {self.nome}>"


class Pagamento(db.Model):
    __tablename__ = "pagamentos"

    id = db.Column(db.Integer, primary_key=True)
    agendamento_id = db.Column(
        db.Integer, db.ForeignKey("agendamentos.id"), nullable=False
    )
    servico_id = db.Column(db.Integer, db.ForeignKey("servicos.id"), nullable=False)
    registrado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    valor = db.Column(db.Float, nullable=False)
    forma_pagamento = db.Column(db.String(20))
    status = db.Column(db.String(20), nullable=False, default="pendente")
    data_vencimento = db.Column(db.Date)
    data_pagamento = db.Column(db.Date)

    agendamento = db.relationship("Agendamento", back_populates="pagamentos")
    servico = db.relationship("Servico", back_populates="pagamentos")
    registrado_por = db.relationship("Usuario")

    @property
    def em_atraso(self):
        return bool(
            self.status == "pendente"
            and self.data_vencimento
            and self.data_vencimento < date.today()
        )

    def __repr__(self):
        return f"<Pagamento {self.id} R$ {self.valor:.2f}>"
