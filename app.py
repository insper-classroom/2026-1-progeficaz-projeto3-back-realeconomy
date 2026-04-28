from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from config import MONGO_URI
from flask_jwt_extended import JWTManager
from config import JWT_SECRET_KEY

from routes.auth import auth_bp

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)

app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)