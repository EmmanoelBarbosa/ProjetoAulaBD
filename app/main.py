from flask import Flask, jsonify, request, Response
from sqlalchemy.orm import joinedload

from app.pdf_service import gerar_relatorio_produtos
from app import sql_service, nosql_service
from app.nosql_service import obter_dashboard_total, registrar_dashboard_total
from models import db, Cliente, Venda
from sql_service import criar_cliente, obter_cliente, listar_clientes, atualizar_cliente, deletar_cliente, listar_produtos, criar_produto, deletar_produto
from config import SQLALCHEMY_DATABASE_URI


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

db.init_app(app)

# Rota principal
@app.route("/")
def index():
    return "API de Vendas em funcionamento."

@app.route("/clientes", methods=["GET"])
def listar_clientes_route():
    clientes = sql_service.listar_clientes()
    return jsonify([{"id_cliente": c.id_cliente, "nome": c.nome, "email": c.email} for c in clientes])

@app.route("/clientes", methods=["POST"])
def criar_cliente_route():
    data = request.json
    if not all(k in data for k in ("nome", "email", "cpf", "data_nascimento")):
        return jsonify({"erro": "Campos obrigatórios: nome, email, cpf, data_nascimento"}), 400

    cliente = sql_service.criar_cliente(**data)
    nosql_service.atualizar_dashboard()
    return jsonify({"id_cliente": cliente.id_cliente, "mensagem": "Cliente criado com sucesso"}), 201

@app.route("/clientes/<int:cliente_id>", methods=["DELETE"])
def deletar_cliente_route(cliente_id):
    cliente = sql_service.deletar_cliente(cliente_id)
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    nosql_service.atualizar_dashboard()
    return jsonify({"mensagem": "Cliente deletado com sucesso"})

@app.route("/clientes/<int:cliente_id>", methods=["PUT"])
def atualizar_cliente_route(cliente_id):
    data = request.json
    cliente = sql_service.atualizar_cliente(cliente_id, **data)
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    nosql_service.atualizar_dashboard()
    return jsonify({"mensagem": "Cliente atualizado com sucesso"})

@app.route("/clientes/<int:cliente_id>", methods=["GET"])
def obter_cliente_route(cliente_id):
    cliente = sql_service.obter_cliente(cliente_id)
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    return jsonify({
        "id_cliente": cliente.id_cliente, "nome": cliente.nome, "email": cliente.email,
        "cpf": cliente.cpf, "data_nascimento": cliente.data_nascimento.strftime("%Y-%m-%d")
    })


# Produtos

@app.route("/produtos", methods=["GET"])
def listar_produtos_route():
    produtos = sql_service.listar_produtos()
    return jsonify([{
        "id_produto": p.id_produto, "nome": p.nome, "preco": p.preco, "estoque": p.estoque
    } for p in produtos])
@app.route("/produtos", methods=["POST"])
def criar_produto_route():
    data = request.json
    produto = sql_service.criar_produto(**data)
    nosql_service.atualizar_dashboard()
    return jsonify({"id_produto": produto.id_produto, "mensagem": "Produto criado com sucesso"}), 201

@app.route("/produtos/<int:produto_id>", methods=["GET"])
def obter_produto_route(produto_id):
    produto = sql_service.obter_produto(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify({
        "id_produto": produto.id_produto, "nome": produto.nome, "preco": produto.preco,
        "estoque": produto.estoque, "descricao": produto.descricao, "categoria": produto.categoria
    })

@app.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto_route(produto_id):
    data = request.json
    produto = sql_service.atualizar_produto(produto_id, **data)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    nosql_service.atualizar_dashboard()
    return jsonify({"mensagem": "Produto atualizado com sucesso"})

@app.route("/produtos/<int:produto_id>", methods=["DELETE"])
def deletar_produto_route(produto_id):
    produto = sql_service.deletar_produto(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    nosql_service.atualizar_dashboard()
    return jsonify({"mensagem": "Produto deletado com sucesso"})
# Vendas

@app.route("/vendas", methods=["GET"])
def listar_vendas_route():
    pedidos = Venda.query.options(
        joinedload(Venda.cliente),
        joinedload(Venda.produto)
    ).all()

    result = []
    for v in pedidos:
        result.append({
            "id": v.id_pedido,
            "data_pedido": v.data_pedido,
            "cliente": v.cliente.nome if v.cliente else None,
            "produto": v.produto.nome if v.produto else None,
            "valor_total": v.valor_total
        })

    return jsonify(result)

@app.route("/vendas", methods=["POST"])
def criar_venda_route():
    data = request.json
    if not all(k in data for k in ("id_cliente", "id_produto", "quantidade")):
        return jsonify({"erro": "Campos obrigatórios: id_cliente, id_produto, quantidade"}), 400

    venda = sql_service.criar_venda(**data)
    if not venda:
        return jsonify({"erro": "Produto inexistente ou estoque insuficiente"}), 400
    nosql_service.atualizar_dashboard()
    return jsonify({"id_venda": venda.id_venda, "mensagem": "Venda registrada com sucesso"}), 201

@app.route("/vendas", methods=["GET"])
def listar_vendas_route():
    vendas = sql_service.listar_vendas()
    return jsonify([{
        "id_venda": v.id_venda, "id_cliente": v.id_cliente, "id_produto": v.id_produto,
        "quantidade": v.quantidade, "valor_total": v.valor_total, "data_venda": v.data_venda.isoformat()
    } for v in vendas])

@app.route("/vendas/<int:venda_id>", methods=["GET"])
def obter_venda_route(venda_id):
    venda = sql_service.obter_venda(venda_id)
    if not venda:
        return jsonify({"erro": "Venda não encontrada"}), 404
    return jsonify({
        "id_venda": venda.id_venda, "id_cliente": venda.id_cliente, "id_produto": venda.id_produto,
        "quantidade": venda.quantidade, "valor_total": venda.valor_total, "data_venda": venda.data_venda.isoformat()
    })

@app.route("/vendas/<int:venda_id>", methods=["DELETE"])
def deletar_venda_route(venda_id):
    venda = sql_service.deletar_venda(venda_id)
    if not venda:
        return jsonify({"erro": "Venda não encontrada"}), 404
    nosql_service.atualizar_dashboard()
    return jsonify({"mensagem": "Venda deletada com sucesso"})

# --- Dashboard e Relatórios ---
@app.route("/dashboard", methods=["GET"])
def obter_dashboard_route():
    dashboard_data = nosql_service.obter_dashboard()
    if not dashboard_data:
        # Se não houver, força a criação
        nosql_service.atualizar_dashboard()
        dashboard_data = nosql_service.obter_dashboard()
    if dashboard_data.get('_id'):
        del dashboard_data['_id'] # Remove o ID interno do Mongo
    return jsonify(dashboard_data)

@app.route("/dashboard/relatorio-pdf", methods=["GET"])
def relatorio_pdf_route():
    dashboard_data = nosql_service.obter_dashboard()
    if not dashboard_data:
        return jsonify({"erro": "Dados do dashboard não encontrados"}), 404

    pdf_bytes = gerar_relatorio_produtos(dashboard_data)

    return Response(pdf_bytes,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=relatorio_produtos.pdf'})


# MongoDB - Relatórios

@app.route("/dashboard/total_clientes", methods=["GET"])
def dashboard_total_clientes():
    total = obter_dashboard_total()
    return jsonify({"total_clientes": total})


if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Cria as tabelas se não existirem
        nosql_service.atualizar_dashboard() # Garante que o dashboard seja criado na inicialização
    app.run(debug=True)