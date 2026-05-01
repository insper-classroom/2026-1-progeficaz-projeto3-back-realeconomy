import pytest
from unittest.mock import patch, MagicMock
from app import app
import bcrypt

@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test_secret"
    with app.test_client() as cliente:
        yield cliente
        
CPF_VALIDO = "111.444.777-35"
CPF_VALIDO_LIMPO = "11144477735"

def test_register_sucesso(cliente):
    with patch('routes.auth.usuarios_collection') as mock_col:
        mock_col.find_one.return_value = None
        mock_col.insert_one.return_value = MagicMock(inserted_id="abc123")

        resposta = cliente.post('/auth/register', json={
            "nome": "Teste",
            "cpf": CPF_VALIDO,
            "senha": "123456"
        })
        assert resposta.status_code == 201
        assert "id" in resposta.get_json()
        
def test_register_cpf_invalido(cliente):
    resposta = cliente.post('/auth/register', json={
        "nome": "Teste",
        "cpf": "11111111111",
        "senha": "123456"
    })
    assert resposta.status_code == 400
    assert resposta.get_json()["erro"] == "CPF inválido"

def test_register_cpf_duplicado(cliente):
    with patch('routes.auth.usuarios_collection') as mock_col:
        mock_col.find_one.return_value = {"cpf": CPF_VALIDO_LIMPO}

        resposta = cliente.post('/auth/register', json={
            "nome": "Teste",
            "cpf": CPF_VALIDO,
            "senha": "123456"
        })
        assert resposta.status_code == 400
        assert resposta.get_json()["erro"] == "CPF já cadastrado"

def test_login_sucesso(cliente):
    senha_hash = bcrypt.hashpw("123456".encode("utf-8"), bcrypt.gensalt())
    with patch('routes.auth.usuarios_collection') as mock_col:
        mock_col.find_one.return_value = {
            "_id": "abc123",
            "nome": "Teste",
            "cpf": CPF_VALIDO_LIMPO,
            "senha": senha_hash,
            "role": "usuario"
        }

        resposta = cliente.post('/auth/login', json={
            "cpf": CPF_VALIDO_LIMPO,
            "senha": "123456"
        })
        assert resposta.status_code == 200
        dados = resposta.get_json()
        assert "access_token" in dados
        assert "refresh_token" in dados

def test_login_senha_incorreta(cliente):
    senha_hash = bcrypt.hashpw("123456".encode("utf-8"), bcrypt.gensalt())
    with patch('routes.auth.usuarios_collection') as mock_col:
        mock_col.find_one.return_value = {
            "_id": "abc123",
            "nome": "Teste",
            "cpf": CPF_VALIDO_LIMPO,
            "senha": senha_hash,
            "role": "usuario"
        }

        resposta = cliente.post('/auth/login', json={
            "cpf": CPF_VALIDO_LIMPO,
            "senha": "senha_errada"
        })
        assert resposta.status_code == 401
        assert resposta.get_json()["erro"] == "Senha incorreta"

def test_login_usuario_nao_encontrado(cliente):
    with patch('routes.auth.usuarios_collection') as mock_col:
        mock_col.find_one.return_value = None

        resposta = cliente.post('/auth/login', json={
            "cpf": CPF_VALIDO_LIMPO,
            "senha": "123456"
        })
        assert resposta.status_code == 404
        assert resposta.get_json()["erro"] == "Usuário não encontrado"
        
def test_refresh_sucesso(cliente):
    senha_hash = bcrypt.hashpw("123456".encode("utf-8"), bcrypt.gensalt())
    with patch('routes.auth.usuarios_collection') as mock_col:
        mock_col.find_one.return_value = {
            "_id": "abc123",
            "nome": "Teste",
            "cpf": CPF_VALIDO_LIMPO,
            "senha": senha_hash,
            "role": "usuario"
        }

        login = cliente.post('/auth/login', json={
            "cpf": CPF_VALIDO_LIMPO,
            "senha": "123456"
        })
        refresh_token = login.get_json()["refresh_token"]

        resposta = cliente.post('/auth/refresh', headers={
            "Authorization": f"Bearer {refresh_token}"
        })
        assert resposta.status_code == 200
        assert "access_token" in resposta.get_json()

def test_refresh_token_invalido(cliente):
    resposta = cliente.post('/auth/refresh', headers={
        "Authorization": "Bearer token_invalido"
    })
    assert resposta.status_code == 422