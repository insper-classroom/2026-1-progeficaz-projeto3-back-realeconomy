from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from database import usuarios_collection
import bcrypt
from utils import validar_cpf

auth_bp = Blueprint("auth", __name__)

# POST /auth/register — cadastro de usuário
@auth_bp.route("/auth/register", methods=["POST"])
def register():
    dados = request.get_json()
    
    if not validar_cpf(dados["cpf"]):
        return jsonify({"erro": "CPF inválido"}), 400

    if usuarios_collection.find_one({"cpf": dados["cpf"]}):
        return jsonify({"erro": "CPF já cadastrado"}), 400

    senha_hash = bcrypt.hashpw(dados["senha"].encode("utf-8"), bcrypt.gensalt())

    usuario = {
        "nome": dados["nome"],
        "cpf": dados["cpf"],
        "senha": senha_hash,
        "role": "usuario"
    }

    resultado = usuarios_collection.insert_one(usuario)
    return jsonify({"mensagem": "Usuário cadastrado com sucesso", "id": str(resultado.inserted_id)}), 201

# POST /auth/login — login do usuário
@auth_bp.route("/auth/login", methods=["POST"])
def login():
    dados = request.get_json()

    usuario = usuarios_collection.find_one({"cpf": dados["cpf"]})
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    if not bcrypt.checkpw(dados["senha"].encode("utf-8"), usuario["senha"]):
        return jsonify({"erro": "Senha incorreta"}), 401

    token = create_access_token(identity=str(usuario["_id"]))
    return jsonify({"token": token, "nome": usuario["nome"]}), 200