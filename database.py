from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.get_database("imoveis")

usuarios_collection = db["usuarios"]
usuarios_collection.create_index("cpf", unique=True) # impede duplicação no db

cidades_collection = db["cidades"]
imoveis_collection = db["imoveis"]

try:
    client.admin.command("ping")
    print("✅ Conectado ao MongoDB!")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")