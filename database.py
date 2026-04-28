from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.get_database("loteria")

usuarios_collection = db["usuarios"]
usuarios_collection.create_index("cpf", unique=True) # impede duplicação no db


try:
    client.admin.command("ping")
    print("✅ Conectado ao MongoDB!")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")