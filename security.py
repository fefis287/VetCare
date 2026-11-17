"""Controle de acesso do VetCare.

A regra central do sistema: a permissão é verificada na rota, não apenas
escondendo botões no HTML. Qualquer rota protegida é decorada com @exige(),
então digitar a URL na mão não contorna nada.

Perfis:
  administrador -> acesso total, incluindo gestão de usuários
  veterinario   -> vê apenas a própria agenda e os prontuários dos seus pacientes
  recepcao      -> agenda, cadastros e financeiro; nunca acessa prontuário
"""

from functools import wraps

from flask import abort, flash, g, redirect, request, session, url_for

from models import Usuario


def usuario_atual():
    """Devolve o usuário da sessão, guardando em g para não repetir consulta."""
    if "usuario" not in g:
        usuario_id = session.get("usuario_id")
        g.usuario = Usuario.query.get(usuario_id) if usuario_id else None
    return g.usuario


def abrir_sessao(usuario):
    session.clear()
    session["usuario_id"] = usuario.id
    g.usuario = usuario


def encerrar_sessao():
    session.clear()
    g.pop("usuario", None)


def exige(*perfis):
    """Protege a rota: exige login e, se perfis forem informados, um deles.

        @exige()                      -> qualquer usuário autenticado
        @exige("administrador")       -> somente administrador
        @exige("veterinario", "recepcao")
    """

    def decorador(rota):
        @wraps(rota)
        def invólucro(*args, **kwargs):
            usuario = usuario_atual()
            if usuario is None:
                flash("Entre no sistema para continuar.", "aviso")
                return redirect(url_for("auth.login", proximo=request.path))
            if not usuario.ativo:
                encerrar_sessao()
                flash("Esse acesso foi desativado. Procure o administrador.", "erro")
                return redirect(url_for("auth.login"))
            if perfis and usuario.perfil not in perfis:
                abort(403)
            return rota(*args, **kwargs)

        return invólucro

    return decorador


def veterinario_da_sessao():
    """Ficha de veterinário do usuário logado, ou None se ele não for um."""
    usuario = usuario_atual()
    return usuario.veterinario if usuario else None


def pode_ver_prontuario(prontuario):
    """Administrador vê tudo; veterinário só o que ele mesmo atendeu."""
    usuario = usuario_atual()
    if usuario is None:
        return False
    if usuario.perfil == "administrador":
        return True
    if usuario.perfil == "veterinario":
        vet = usuario.veterinario
        return bool(vet and prontuario.veterinario_id == vet.id)
    return False


def pode_atender(agendamento):
    """Quem pode registrar o atendimento desse agendamento."""
    usuario = usuario_atual()
    if usuario is None:
        return False
    if usuario.perfil == "administrador":
        return True
    if usuario.perfil == "veterinario":
        vet = usuario.veterinario
        return bool(vet and agendamento.veterinario_id == vet.id)
    return False
