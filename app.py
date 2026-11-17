"""VetCare — sistema de gestão para clínica veterinária.

Para rodar:

    python -m pip install -r requirements.txt
    python seed.py      (só na primeira vez, cria o banco com dados de teste)
    python app.py

Depois abra http://127.0.0.1:5000 no navegador.
"""

import os
from datetime import date, datetime

from flask import Flask, render_template

from extensions import db
from security import usuario_atual

PASTA_BASE = os.path.abspath(os.path.dirname(__file__))
CAMINHO_BANCO = os.path.join(PASTA_BASE, "vetcare.db")


def criar_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("VETCARE_SECRET", "vetcare-dev-2026")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{CAMINHO_BANCO}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # ---- blueprints
    from blueprints.auth import bp as bp_auth
    from blueprints.painel import bp as bp_painel
    from blueprints.cadastros import bp as bp_cadastros
    from blueprints.agenda import bp as bp_agenda
    from blueprints.clinico import bp as bp_clinico
    from blueprints.financeiro import bp as bp_financeiro
    from blueprints.admin import bp as bp_admin

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_painel)
    app.register_blueprint(bp_cadastros)
    app.register_blueprint(bp_agenda)
    app.register_blueprint(bp_clinico)
    app.register_blueprint(bp_financeiro)
    app.register_blueprint(bp_admin)

    # ---- tudo que os templates precisam enxergar
    @app.context_processor
    def variaveis_globais():
        return {"usuario": usuario_atual(), "hoje": date.today()}

    @app.template_filter("data")
    def filtro_data(valor):
        if valor is None:
            return "—"
        return valor.strftime("%d/%m/%Y")

    @app.template_filter("datahora")
    def filtro_datahora(valor):
        if valor is None:
            return "—"
        return valor.strftime("%d/%m/%Y às %H:%M")

    @app.template_filter("dinheiro")
    def filtro_dinheiro(valor):
        return f"R$ {valor or 0:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # ---- erros
    @app.errorhandler(403)
    def sem_permissao(_):
        return render_template("erro.html", codigo=403,
                               titulo="Esta área não faz parte do seu perfil",
                               detalhe="Se você precisa desse acesso, peça ao "
                                       "administrador para ajustar seu perfil."), 403

    @app.errorhandler(404)
    def nao_encontrado(_):
        return render_template("erro.html", codigo=404,
                               titulo="Página não encontrada",
                               detalhe="O endereço digitado não existe no sistema."), 404

    return app


app = criar_app()


if __name__ == "__main__":
    if not os.path.exists(CAMINHO_BANCO):
        print("\n[VetCare] O banco vetcare.db ainda não existe.")
        print("[VetCare] Rode 'python seed.py' antes de iniciar o servidor.\n")
    app.run(debug=True)
