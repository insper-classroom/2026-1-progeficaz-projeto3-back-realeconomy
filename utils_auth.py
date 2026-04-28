from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from database import usuarios_collection
from bson import ObjectId

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        usuario_id = get_jwt_identity()
        usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
        if not usuario or usuario.get("role") != "admin":
            return jsonify({"erro": "Acesso negado"}), 403
        return fn(*args, **kwargs)
    return wrapper