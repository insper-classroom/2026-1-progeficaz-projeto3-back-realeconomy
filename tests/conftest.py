import pytest
from app import app
from database import usuarios_collection, imoveis_collection, cidades_collection

@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test_secret"
    with app.test_client() as cliente:
        yield cliente

@pytest.fixture(autouse=True)
def limpar_banco():
    yield
    usuarios_collection.delete_many({"cpf": "52998224725"})
    imoveis_collection.delete_many({"descricao": "teste"})