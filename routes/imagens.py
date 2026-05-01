from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
import cloudinary
import cloudinary.uploader
from config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

imagens_bp = Blueprint("imagens", __name__)

# POST /imagens — faz upload de uma imagem
@imagens_bp.route("/imagens", methods=["POST"])
@jwt_required()
def upload_imagem():
    if 'imagem' not in request.files:
        return jsonify({"erro": "Nenhuma imagem enviada"}), 400

    arquivo = request.files['imagem']

    if arquivo.filename == '':
        return jsonify({"erro": "Nenhuma imagem selecionada"}), 400

    try:
        resultado = cloudinary.uploader.upload(
            arquivo,
            folder="realeconomy"
        )
        return jsonify({"url": resultado["secure_url"]}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500