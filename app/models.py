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
    __tablename__ = "produtos"

    id_produto = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(500), nullable=True)
    categoria = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Produto {self.nome}>"

class Venda(db.Model):
    __tablename__ = "pedidos"

    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("clientes.id_cliente"), nullable=False)
    id_produto = db.Column(db.Integer, db.ForeignKey("produtos.id_produto"), nullable=False)
    data_pedido = db.Column(db.DateTime, server_default=func.now())
    valor_total = db.Column(db.Float(10), nullable=False)

    # Relacionamentos (apenas aqui, para evitar conflito)
    cliente = db.relationship("Cliente", backref="pedidos")
    produto = db.relationship("Produto", backref="pedidos")

    def __repr__(self):
        return f"<Venda {self.id} - Cliente {self.cliente_id} - Produto {self.produto_id}>"
