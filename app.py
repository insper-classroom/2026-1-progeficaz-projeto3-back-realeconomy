from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from config import MONGO_URI

app = Flask(__name__)
CORS(app)

client = MongoClient(MONGO_URI)

try:
    client.admin.command("ping")
    print("✅ Conectado ao MongoDB!")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    app.run(debug=True)