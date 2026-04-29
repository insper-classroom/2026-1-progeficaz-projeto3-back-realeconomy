from flask import Blueprint, jsonify, request
from bson import ObjectId
from database import cidades_collection
from utils_auth import admin_required
from flask_jwt_extended import jwt_required

cidades_bp = Blueprint("cidades", __name__)

def serializar(cidade):
    cidade["_id"] = str(cidade["_id"])
    return cidade

# GET /cidades — lista todas as cidades (público)
@cidades_bp.route("/cidades", methods=["GET"])
def listar_cidades():
    cidades = list(cidades_collection.find())
    return jsonify([serializar(c) for c in cidades]), 200

# POST /cidades — cria cidade (admin)
@cidades_bp.route("/cidades", methods=["POST"])
@admin_required
def criar_cidade():
    dados = request.get_json()

    if not dados.get("nome"):
        return jsonify({"erro": "Nome da cidade é obrigatório"}), 400

    if cidades_collection.find_one({"nome": dados["nome"]}):
        return jsonify({"erro": "Cidade já cadastrada"}), 400

    cidade = {
        "nome": dados["nome"],
        "estado": dados.get("estado", "")
    }

    resultado = cidades_collection.insert_one(cidade)
    cidade["_id"] = str(resultado.inserted_id)
    return jsonify(cidade), 201

# DELETE /cidades/<id> — remove cidade (admin)
@cidades_bp.route("/cidades/<id>", methods=["DELETE"])
@admin_required
def deletar_cidade(id):
    resultado = cidades_collection.delete_one({"_id": ObjectId(id)})
    if resultado.deleted_count == 0:
        return jsonify({"erro": "Cidade não encontrada"}), 404
    return jsonify({"mensagem": "Cidade removida com sucesso"}), 200