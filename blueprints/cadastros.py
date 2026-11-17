"""Tutores, animais e veterinários."""

from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from extensions import db
from models import Animal, Especie, Raca, Tutor, Usuario, Veterinario
from security import exige, usuario_atual

bp = Blueprint("cadastros", __name__)


def _data(campo):
    texto = request.form.get(campo, "").strip()
    if not texto:
        return None
    return datetime.strptime(texto, "%Y-%m-%d").date()


def _numero(campo):
    texto = request.form.get(campo, "").strip().replace(",", ".")
    return float(texto) if texto else None


# --------------------------------------------------------------------- tutores
@bp.route("/tutores")
@exige("administrador", "recepcao", "veterinario")
def tutores():
    busca = request.args.get("busca", "").strip()
    consulta = Tutor.query
    if busca:
        filtro = f"%{busca}%"
        consulta = consulta.filter(
            db.or_(Tutor.nome.ilike(filtro), Tutor.cpf.ilike(filtro))
        )
    lista = consulta.order_by(Tutor.nome).all()
    return render_template("tutores/lista.html", tutores=lista, busca=busca)


@bp.route("/tutores/novo", methods=["GET", "POST"])
@bp.route("/tutores/<int:tutor_id>/editar", methods=["GET", "POST"])
@exige("administrador", "recepcao")
def form_tutor(tutor_id=None):
    tutor = Tutor.query.get_or_404(tutor_id) if tutor_id else None

    if request.method == "POST":
        cpf = request.form["cpf"].strip()
        repetido = Tutor.query.filter_by(cpf=cpf).first()
        if repetido and (tutor is None or repetido.id != tutor.id):
            flash("Já existe um tutor cadastrado com esse CPF.", "erro")
            return render_template("tutores/form.html", tutor=tutor)

        if tutor is None:
            tutor = Tutor()
            db.session.add(tutor)

        tutor.nome = request.form["nome"].strip()
        tutor.cpf = cpf
        tutor.telefone = request.form["telefone"].strip()
        tutor.email = request.form.get("email", "").strip() or None
        tutor.endereco = request.form.get("endereco", "").strip() or None
        tutor.ativo = bool(request.form.get("ativo"))
        db.session.commit()
        flash("Tutor salvo.", "ok")
        return redirect(url_for("cadastros.ficha_tutor", tutor_id=tutor.id))

    return render_template("tutores/form.html", tutor=tutor)


@bp.route("/tutores/<int:tutor_id>")
@exige("administrador", "recepcao", "veterinario")
def ficha_tutor(tutor_id):
    tutor = Tutor.query.get_or_404(tutor_id)
    return render_template("tutores/ficha.html", tutor=tutor)


# --------------------------------------------------------------------- animais
@bp.route("/animais")
@exige("administrador", "recepcao", "veterinario")
def animais():
    busca = request.args.get("busca", "").strip()
    consulta = Animal.query.join(Tutor)
    if busca:
        filtro = f"%{busca}%"
        consulta = consulta.filter(
            db.or_(Animal.nome.ilike(filtro), Tutor.nome.ilike(filtro))
        )
    lista = consulta.order_by(Animal.nome).all()
    return render_template("animais/lista.html", animais=lista, busca=busca)


@bp.route("/animais/novo", methods=["GET", "POST"])
@bp.route("/animais/<int:animal_id>/editar", methods=["GET", "POST"])
@exige("administrador", "recepcao")
def form_animal(animal_id=None):
    animal = Animal.query.get_or_404(animal_id) if animal_id else None
    tutores = Tutor.query.filter_by(ativo=True).order_by(Tutor.nome).all()
    especies = Especie.query.order_by(Especie.nome).all()
    racas = Raca.query.order_by(Raca.nome).all()

    if request.method == "POST":
        if animal is None:
            animal = Animal()
            db.session.add(animal)

        animal.nome = request.form["nome"].strip()
        animal.tutor_id = int(request.form["tutor_id"])
        animal.especie_id = int(request.form["especie_id"])
        raca_id = request.form.get("raca_id")
        animal.raca_id = int(raca_id) if raca_id else None
        animal.sexo = request.form.get("sexo") or None
        animal.data_nascimento = _data("data_nascimento")
        animal.peso = _numero("peso")
        animal.pelagem = request.form.get("pelagem", "").strip() or None
        animal.observacoes = request.form.get("observacoes", "").strip() or None
        animal.ativo = bool(request.form.get("ativo"))
        db.session.commit()
        flash("Animal salvo.", "ok")
        return redirect(url_for("cadastros.ficha_animal", animal_id=animal.id))

    tutor_sugerido = request.args.get("tutor_id", type=int)
    return render_template(
        "animais/form.html",
        animal=animal,
        tutores=tutores,
        especies=especies,
        racas=racas,
        tutor_sugerido=tutor_sugerido,
    )


@bp.route("/animais/<int:animal_id>")
@exige("administrador", "recepcao", "veterinario")
def ficha_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    usuario = usuario_atual()

    # A recepção não vê prontuário em lugar nenhum, nem aqui na ficha.
    prontuarios = []
    if usuario.perfil == "administrador":
        prontuarios = sorted(animal.prontuarios, key=lambda p: p.data, reverse=True)
    elif usuario.perfil == "veterinario" and usuario.veterinario:
        prontuarios = sorted(
            [p for p in animal.prontuarios
             if p.veterinario_id == usuario.veterinario.id],
            key=lambda p: p.data,
            reverse=True,
        )

    aplicacoes = sorted(
        animal.aplicacoes, key=lambda a: a.data_aplicacao, reverse=True
    )
    agendamentos = sorted(
        animal.agendamentos, key=lambda a: a.data_hora, reverse=True
    )[:10]

    return render_template(
        "animais/ficha.html",
        animal=animal,
        prontuarios=prontuarios,
        aplicacoes=aplicacoes,
        agendamentos=agendamentos,
    )


# ---------------------------------------------------------------- veterinários
@bp.route("/veterinarios")
@exige("administrador", "recepcao")
def veterinarios():
    lista = Veterinario.query.join(Usuario).order_by(Usuario.nome).all()
    return render_template("veterinarios/lista.html", veterinarios=lista)


@bp.route("/veterinarios/novo", methods=["GET", "POST"])
@bp.route("/veterinarios/<int:vet_id>/editar", methods=["GET", "POST"])
@exige("administrador")
def form_veterinario(vet_id=None):
    vet = Veterinario.query.get_or_404(vet_id) if vet_id else None

    if request.method == "POST":
        crmv = request.form["crmv"].strip()
        repetido = Veterinario.query.filter_by(crmv=crmv).first()
        if repetido and (vet is None or repetido.id != vet.id):
            flash("Já existe um veterinário com esse CRMV.", "erro")
            return render_template("veterinarios/form.html", vet=vet)

        if vet is None:
            email = request.form["email"].strip().lower()
            if Usuario.query.filter_by(email=email).first():
                flash("Já existe um usuário com esse e-mail.", "erro")
                return render_template("veterinarios/form.html", vet=vet)

            usuario = Usuario(
                nome=request.form["nome"].strip(),
                email=email,
                perfil="veterinario",
            )
            usuario.definir_senha(request.form.get("senha") or "123456")
            db.session.add(usuario)
            db.session.flush()

            vet = Veterinario(usuario_id=usuario.id)
            db.session.add(vet)
        else:
            vet.usuario.nome = request.form["nome"].strip()

        vet.crmv = crmv
        vet.especialidade = request.form.get("especialidade", "").strip() or None
        vet.telefone = request.form.get("telefone", "").strip() or None
        db.session.commit()
        flash("Veterinário salvo.", "ok")
        return redirect(url_for("cadastros.veterinarios"))

    return render_template("veterinarios/form.html", vet=vet)
