from datetime import datetime
from models import Cliente, db, Produto, Venda


def criar_cliente(nome, email, cpf, data_nascimento):
    cliente = Cliente(
        nome=nome,
        email=email,
        cpf=cpf,
        data_nascimento=datetime.strptime(data_nascimento, "%Y-%m-%d").date()
    )
    db.session.add(cliente)
    db.session.commit()
    return cliente

def listar_clientes():
    return Cliente.query.all()

def obter_cliente(cliente_id):
    return Cliente.query.get(cliente_id)

def deletar_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return None
    db.session.delete(cliente)
    db.session.commit()
    return cliente

def atualizar_cliente(cliente_id, nome=None, email=None,
                      cpf=None, data_nascimento=None):
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return None
    if nome:
        cliente.nome = nome
    if email:
        cliente.email = email
    if cpf:
        cliente.cpf = cpf
    if data_nascimento:
        cliente.data_nascimento = datetime.strptime(
            data_nascimento, "%Y-%m-%d").date()
    db.session.commit()
    return cliente

# ----------------- PRODUTOS -----------------
def criar_produto(nome, preco, descricao, categoria, estoque):
    produto = Produto(nome=nome, preco=preco, descricao=descricao, categoria=categoria, estoque=estoque)
    db.session.add(produto)
    db.session.commit()
    return produto

def listar_produtos():
    return Produto.query.all()

def obter_produto(produto_id):
    return Produto.query.get(produto_id)

def atualizar_produto(produto_id, nome, preco, descricao, categoria, estoque):
    produto = Produto.query.get(produto_id)
    if produto:
        produto.nome = nome
        produto.preco = preco
        produto.descricao = descricao
        produto.categoria = categoria
        produto.estoque = estoque
        db.session.commit()
    return produto

def deletar_produto(id):
    produto = Produto.query.get(id)
    if produto:
        db.session.delete(produto)
        db.session.commit()
    return produto

# ----------------- VENDAS -----------------
def criar_venda(id_cliente, id_produto, quantidade):
    produto = Produto.query.get(id_produto)
    if not produto or produto.estoque < quantidade:
        return None  # Produto não existe ou não tem estoque

    valor_total = produto.preco * quantidade
    venda = Venda(id_cliente=id_cliente, id_produto=id_produto, quantidade=quantidade, valor_total=valor_total)
    produto.estoque -= quantidade  # Baixa no estoque
    db.session.add(venda)
    db.session.commit()
    return venda

def listar_vendas():
    return Venda.query.all()

def obter_venda(venda_id):
    return Venda.query.get(venda_id)

def deletar_venda(venda_id):
    venda = Venda.query.get(venda_id)
    if not venda:
        return None

    produto = Produto.query.get(venda.id_produto)
    if produto:
        produto.estoque += venda.quantidade  # Devolve ao estoque

    db.session.delete(venda)
    db.session.commit()
    return venda