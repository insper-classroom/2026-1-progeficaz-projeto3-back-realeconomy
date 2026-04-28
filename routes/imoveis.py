from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from database import imoveis_collection
import requests

imoveis_bp = Blueprint("imoveis", __name__)

TIPOS_IMOVEL = ["casa", "apartamento", "terreno", "comercial", "chacara", "imóvel rural"]
TIPOS_NEGOCIO = ["venda", "aluguel"]

def serializar(imovel):
    imovel["_id"] = str(imovel["_id"])
    imovel["usuario_id"] = str(imovel["usuario_id"])
    return imovel

# GET /imoveis — lista imóveis com filtros
@imoveis_bp.route("/imoveis", methods=["GET"])
def listar_imoveis():
    filtros = {}

    cidade = request.args.get("cidade")
    tipo_negocio = request.args.get("tipo_negocio")
    tipo_imovel = request.args.get("tipo_imovel")
    preco_min = request.args.get("preco_min")
    preco_max = request.args.get("preco_max")

    if cidade:
        filtros["cidade"] = {"$regex": cidade, "$options": "i"}
    if tipo_negocio:
        filtros["tipo_negocio"] = tipo_negocio
    if tipo_imovel:
        filtros["tipo_imovel"] = tipo_imovel
    if preco_min or preco_max:
        filtros["preco"] = {}
        if preco_min:
            filtros["preco"]["$gte"] = float(preco_min)
        if preco_max:
            filtros["preco"]["$lte"] = float(preco_max)

    imoveis = list(imoveis_collection.find(filtros))
    return jsonify([serializar(i) for i in imoveis]), 200

# POST /imoveis — cadastra um imóvel
@imoveis_bp.route("/imoveis", methods=["POST"])
@jwt_required()
def criar_imovel():
    usuario_id = get_jwt_identity()
    dados = request.get_json()

    # Validações
    tipo_negocio = dados["tipo_negocio"]
    if not isinstance(tipo_negocio, list) or not all(t in TIPOS_NEGOCIO for t in tipo_negocio):
        return jsonify({"erro": "tipo_negocio inválido"}), 400
    if "venda" not in tipo_negocio and "aluguel" not in tipo_negocio:
        return jsonify({"erro": "Informe pelo menos um tipo de negócio"}), 400
    if "venda" in tipo_negocio and "preco_venda" not in dados:
        return jsonify({"erro": "Informe o preço de venda"}), 400
    if "aluguel" in tipo_negocio and "preco_aluguel" not in dados:
        return jsonify({"erro": "Informe o preço de aluguel"}), 400

    # Consulta ViaCEP
    try:
        cep = ''.join(filter(str.isdigit, dados["cep"]))
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        endereco = response.json()
        if "erro" in endereco:
            return jsonify({"erro": "CEP não encontrado"}), 400
    except Exception as e:
        return jsonify({"erro": f"Erro ao consultar CEP: {str(e)}"}), 500

    imovel = {
        "usuario_id": ObjectId(usuario_id),
        "tipo_negocio": dados["tipo_negocio"],
        "tipo_imovel": dados["tipo_imovel"],
        "preco_venda": float(dados["preco_venda"]) if "venda" in tipo_negocio else None,
        "preco_aluguel": float(dados["preco_aluguel"]) if "aluguel" in tipo_negocio else None, 
        "cep": cep,
        "logradouro": endereco["logradouro"],
        "numero": dados["numero"],
        "bairro": endereco["bairro"],
        "cidade": endereco["localidade"],
        "estado": endereco["uf"],
        "descricao": dados.get("descricao", "")
    }

    resultado = imoveis_collection.insert_one(imovel)
    imovel["_id"] = str(resultado.inserted_id)
    imovel["usuario_id"] = usuario_id
    return jsonify(imovel), 201

# PUT /imoveis/<id> — edita um imóvel
@imoveis_bp.route("/imoveis/<id>", methods=["PUT"])
@jwt_required()
def editar_imovel(id):
    usuario_id = get_jwt_identity()
    dados = request.get_json()

    imovel = imoveis_collection.find_one({"_id": ObjectId(id)})
    if not imovel:
        return jsonify({"erro": "Imóvel não encontrado"}), 404
    if str(imovel["usuario_id"]) != usuario_id:
        return jsonify({"erro": "Sem permissão para editar este imóvel"}), 403

    atualizacao = {}

    if "tipo_negocio" in dados:
        tipo_negocio = dados["tipo_negocio"]
        if not isinstance(tipo_negocio, list) or not all(t in TIPOS_NEGOCIO for t in tipo_negocio):
            return jsonify({"erro": "tipo_negocio inválido"}), 400
        atualizacao["tipo_negocio"] = tipo_negocio

        if "preco_venda" in dados:
            atualizacao["preco_venda"] = float(dados["preco_venda"])

        if "preco_aluguel" in dados:
            atualizacao["preco_aluguel"] = float(dados["preco_aluguel"])
        
    if "tipo_imovel" in dados:
        if dados["tipo_imovel"] not in TIPOS_IMOVEL:
            return jsonify({"erro": "tipo_imovel inválido"}), 400
        atualizacao["tipo_imovel"] = dados["tipo_imovel"]

    if "preco" in dados:
        atualizacao["preco"] = float(dados["preco"])

    if "numero" in dados:
        atualizacao["numero"] = dados["numero"]

    if "descricao" in dados:
        atualizacao["descricao"] = dados["descricao"]

    if "cep" in dados:
        try:
            cep = ''.join(filter(str.isdigit, dados["cep"]))
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            endereco = response.json()
            if "erro" in endereco:
                return jsonify({"erro": "CEP não encontrado"}), 400
            atualizacao["cep"] = cep
            atualizacao["logradouro"] = endereco["logradouro"]
            atualizacao["bairro"] = endereco["bairro"]
            atualizacao["cidade"] = endereco["localidade"]
            atualizacao["estado"] = endereco["uf"]
        except Exception as e:
            return jsonify({"erro": f"Erro ao consultar CEP: {str(e)}"}), 500

    imoveis_collection.update_one({"_id": ObjectId(id)}, {"$set": atualizacao})
    imovel_atualizado = imoveis_collection.find_one({"_id": ObjectId(id)})
    return jsonify({"mensagem": "Imóvel atualizado com sucesso.", "imóvel": serializar(imovel_atualizado)}), 200

# DELETE /imoveis/<id> — remove um imóvel
@imoveis_bp.route("/imoveis/<id>", methods=["DELETE"])
@jwt_required()
def deletar_imovel(id):
    usuario_id = get_jwt_identity()

    imovel = imoveis_collection.find_one({"_id": ObjectId(id)})
    if not imovel:
        return jsonify({"erro": "Imóvel não encontrado."}), 404
    if str(imovel["usuario_id"]) != usuario_id:
        return jsonify({"erro": "Sem permissão para deletar este imóvel."}), 403

    imoveis_collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"mensagem": "Imóvel removido com sucesso"}), 200