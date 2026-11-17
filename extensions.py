"""Extensões compartilhadas.

Mantemos a instância do SQLAlchemy em um módulo separado para que os models e
os blueprints possam importá-la sem criar importação circular com o app.py.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
