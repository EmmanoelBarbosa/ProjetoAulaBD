from pymongo import MongoClient

from config import MONGO_URL, MONGO_DB, MONGO_COLLECTION

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=2000)
    client.server_info()
    mongo_db = client[MONGO_DB]
    dashboard_collection = mongo_db[MONGO_COLLECTION]
    mongo_connected = True
    print("[MongoDB] Conectado com sucesso!")
except Exception as e:
    print(f"[MongoDB] Aviso: não foi possível conectar: {e}")
    mongo_db = None
    dashboard_collection = None
    mongo_connected = False

def registrar_documento(collection_name, filtro, valores):
    if mongo_connected:
        collection = mongo_db[collection_name]
        collection.update_one(filtro,
                              {"$set": valores}, upsert=True)

    else:
        print("[MongoDB] Registro ignorado (sem conexão)")

def obter_documento(collection_name, filtro):
    if mongo_connected:
        collection = mongo_db[collection_name]
        return collection.find_one(filtro)
    return None

def registrar_dashboard_total(total_clientes):
    if mongo_connected:
        dashboard_collection.update_one(
            {"_id": "total_clientes"},
            {"$set": {"total": total_clientes}},
            upsert=True
        )
    else:
        print("[MongoDB] Registro ignorado (sem conexão)")

def obter_dashboard_total():
    if mongo_connected:
        doc = dashboard_collection.find_one({"_id": "total_clientes"})
        return doc["total"] if doc else 0
    return 0