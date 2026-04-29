from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRES, REFRESH_TOKEN_EXPIRES

from routes.auth import auth_bp
from routes.imoveis import imoveis_bp
from routes.cidades import cidades_bp

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_TOKEN_EXPIRES
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = REFRESH_TOKEN_EXPIRES

app.register_blueprint(auth_bp)
app.register_blueprint(imoveis_bp)
app.register_blueprint(cidades_bp)

if __name__ == "__main__":
    app.run(debug=True)