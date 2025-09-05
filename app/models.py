from sqlalchemy.sql import func

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = "clientes"

    id_cliente = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)

class Produto(db.Model):
    _tablename_ = "produtos"

    id_produto = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, nullable=False, default=0)
    descricao = db.Column(db.String(500), nullable=True)
    categoria = db.Column(db.String(100), nullable=True)

    def _repr_(self):
        return f"<Produto {self.nome}>"

class Venda(db.Model):
    _tablename_ = "vendas"

    id_venda = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("clientes.id_cliente"), nullable=False)
    id_produto = db.Column(db.Integer, db.ForeignKey("produtos.id_produto"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_venda = db.Column(db.DateTime, server_default=func.now())
    valor_total = db.Column(db.Float(10), nullable=False)

    # Relacionamentos (apenas aqui, para evitar conflito)
    cliente = db.relationship("Cliente", backref="vendas")
    produto = db.relationship("Produto", backref="vendas")

    def _repr_(self):
        return f"<Venda {self.id_venda} - Cliente {self.id_cliente} - Produto {self.id_produto}>"
