from pymongo import MongoClient
from sqlalchemy import func

from config import MONGO_URL, MONGO_DB, MONGO_COLLECTION
from models import db, Cliente, Produto, Venda

# Constante global para o dashboard
DASHBOARD_ID = "dashboard_geral"

# Conexão com MongoDB
try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=2000)
    client.server_info()  # Testa conexão
    mongo_db = client[MONGO_DB]
    dashboard_collection = mongo_db[MONGO_COLLECTION]
    mongo_connected = True
    print("[MongoDB] Conectado com sucesso!")
except Exception as e:
    print(f"[MongoDB] Aviso: não foi possível conectar: {e}")
    mongo_db = None
    dashboard_collection = None
    mongo_connected = False


def atualizar_dashboard():
    """Atualiza o dashboard geral no MongoDB com dados do SQLAlchemy."""
    if not mongo_connected:
        print("[MongoDB] Atualização do dashboard ignorada (sem conexão)")
        return

    from main import app
    with app.app_context():
        # Totais
        total_clientes = db.session.query(func.count(Cliente.id_cliente)).scalar()
        total_produtos = db.session.query(func.count(Produto.id_produto)).scalar()
        total_vendas = db.session.query(func.count(Venda.id_venda)).scalar()
        receita_total = db.session.query(func.sum(Venda.valor_total)).scalar() or 0

        # Top 5 produtos mais vendidos
        produtos_mais_vendidos_query = (
            db.session.query(
                Produto.nome,
                func.sum(Venda.quantidade).label('total_vendido')
            )
            .join(Venda, Produto.id_produto == Venda.id_produto)
            .group_by(Produto.nome)
            .order_by(func.sum(Venda.quantidade).desc())
            .limit(5)
            .all()
        )

        produtos_mais_vendidos = [
            {"nome": nome, "total_vendido": int(total)}
            for nome, total in produtos_mais_vendidos_query
        ]

        # Documento do dashboard
        dashboard_data = {
            "total_clientes": total_clientes,
            "total_produtos": total_produtos,
            "total_vendas": total_vendas,
            "receita_total": float(receita_total),
            "produtos_mais_vendidos": produtos_mais_vendidos,
        }

        # Atualiza ou cria o documento no MongoDB
        dashboard_collection.update_one(
            {"_id": DASHBOARD_ID},
            {"$set": dashboard_data},
            upsert=True
        )
        print("[MongoDB] Dashboard atualizado com sucesso!")


def obter_dashboard():
    """Retorna o dashboard geral do MongoDB."""
    if mongo_connected:
        dashboard = dashboard_collection.find_one({"_id": DASHBOARD_ID})
        if dashboard and 'receita_total' in dashboard:
            dashboard['receita_total'] = float(dashboard['receita_total'])
        return dashboard
    return None


def registrar_documento(collection_name, filtro, valores):
    """Registra ou atualiza um documento em qualquer coleção."""
    if mongo_connected:
        collection = mongo_db[collection_name]
        collection.update_one(filtro, {"$set": valores}, upsert=True)
    else:
        print("[MongoDB] Registro ignorado (sem conexão)")


def obter_documento(collection_name, filtro):
    """Busca um documento em qualquer coleção."""
    if mongo_connected:
        collection = mongo_db[collection_name]
        return collection.find_one(filtro)
    return None


def registrar_dashboard_total(total_clientes):
    """Registra o total de clientes separadamente no MongoDB."""
    if mongo_connected:
        dashboard_collection.update_one(
            {"_id": "total_clientes"},
            {"$set": {"total": total_clientes}},
            upsert=True
        )
    else:
        print("[MongoDB] Registro ignorado (sem conexão)")


def obter_dashboard_total():
    """Retorna o total de clientes registrado no MongoDB."""
    if mongo_connected:
        doc = dashboard_collection.find_one({"_id": "total_clientes"})
        return doc["total"] if doc else 0
    return 0