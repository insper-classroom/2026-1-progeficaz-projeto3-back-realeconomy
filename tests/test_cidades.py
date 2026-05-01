from unittest.mock import patch, MagicMock
from bson import ObjectId
import bcrypt

CPF_VALIDO_LIMPO = "11144477735"
USUARIO_ID = str(ObjectId())

CIDADE_MOCK = {
    "_id": ObjectId(),
    "nome": "São Paulo",
    "estado": "SP"
}

def get_token_admin(cliente):
    senha_hash = bcrypt.hashpw("123456".encode("utf-8"), bcrypt.gensalt())
    with patch('routes.auth.usuarios_collection') as mock_col:
        mock_col.find_one.return_value = {
            "_id": ObjectId(USUARIO_ID),
            "nome": "Admin",
            "cpf": CPF_VALIDO_LIMPO,
            "senha": senha_hash,
            "role": "admin"
        }
        resposta = cliente.post('/auth/login', json={
            "cpf": CPF_VALIDO_LIMPO,
            "senha": "123456"
        })
        return resposta.get_json()["access_token"]

def get_token_usuario(cliente):
    senha_hash = bcrypt.hashpw("123456".encode("utf-8"), bcrypt.gensalt())
    with patch('routes.auth.usuarios_collection') as mock_col:
        mock_col.find_one.return_value = {
            "_id": ObjectId(USUARIO_ID),
            "nome": "Teste",
            "cpf": CPF_VALIDO_LIMPO,
            "senha": senha_hash,
            "role": "usuario"
        }
        resposta = cliente.post('/auth/login', json={
            "cpf": CPF_VALIDO_LIMPO,
            "senha": "123456"
        })
        return resposta.get_json()["access_token"]

def test_listar_cidades(cliente):
    with patch('routes.cidades.cidades_collection') as mock_col:
        mock_col.find.return_value = [CIDADE_MOCK]

        resposta = cliente.get('/cidades')
        assert resposta.status_code == 200
        assert len(resposta.get_json()) == 1

def test_listar_cidades_vazio(cliente):
    with patch('routes.cidades.cidades_collection') as mock_col:
        mock_col.find.return_value = []

        resposta = cliente.get('/cidades')
        assert resposta.status_code == 200
        assert len(resposta.get_json()) == 0

def test_criar_cidade_admin(cliente):
    token = get_token_admin(cliente)
    with patch('routes.cidades.cidades_collection') as mock_col, \
         patch('utils_auth.usuarios_collection') as mock_usuarios:

        mock_usuarios.find_one.return_value = {
            "_id": ObjectId(USUARIO_ID),
            "role": "admin"
        }
        mock_col.find_one.return_value = None
        mock_col.insert_one.return_value = MagicMock(inserted_id=ObjectId())

        resposta = cliente.post('/cidades',
            json={"nome": "São Paulo", "estado": "SP"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 201

def test_criar_cidade_usuario_comum(cliente):
    token = get_token_usuario(cliente)
    with patch('utils_auth.usuarios_collection') as mock_usuarios:
        mock_usuarios.find_one.return_value = {
            "_id": ObjectId(USUARIO_ID),
            "role": "usuario"
        }

        resposta = cliente.post('/cidades',
            json={"nome": "São Paulo", "estado": "SP"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 403

def test_criar_cidade_sem_token(cliente):
    resposta = cliente.post('/cidades',
        json={"nome": "São Paulo", "estado": "SP"}
    )
    assert resposta.status_code == 401

def test_criar_cidade_duplicada(cliente):
    token = get_token_admin(cliente)
    with patch('utils_auth.usuarios_collection') as mock_col, \
         patch('utils_auth.usuarios_collection') as mock_usuarios:

        mock_usuarios.find_one.return_value = {
            "_id": ObjectId(USUARIO_ID),
            "role": "admin"
        }
        mock_col.find_one.return_value = CIDADE_MOCK

        resposta = cliente.post('/cidades',
            json={"nome": "São Paulo", "estado": "SP"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 400
        assert resposta.get_json()["erro"] == "Cidade já cadastrada"

def test_criar_cidade_sem_nome(cliente):
    token = get_token_admin(cliente)
    with patch('utils_auth.usuarios_collection') as mock_col, \
         patch('utils_auth.usuarios_collection') as mock_usuarios:

        mock_usuarios.find_one.return_value = {
            "_id": ObjectId(USUARIO_ID),
            "role": "admin"
        }
        mock_col.find_one.return_value = None

        resposta = cliente.post('/cidades',
            json={"estado": "SP"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 400
        assert resposta.get_json()["erro"] == "Nome da cidade é obrigatório"

def test_deletar_cidade_admin(cliente):
    token = get_token_admin(cliente)
    with patch('routes.cidades.cidades_collection') as mock_col, \
         patch('utils_auth.usuarios_collection') as mock_usuarios:

        mock_usuarios.find_one.return_value = {
            "_id": ObjectId(USUARIO_ID),
            "role": "admin"
        }
        mock_col.delete_one.return_value = MagicMock(deleted_count=1)

        resposta = cliente.delete(
            f'/cidades/{str(CIDADE_MOCK["_id"])}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 200

def test_deletar_cidade_nao_encontrada(cliente):
    token = get_token_admin(cliente)
    with patch('routes.cidades.cidades_collection') as mock_col, \
         patch('utils_auth.usuarios_collection') as mock_usuarios:

        mock_usuarios.find_one.return_value = {
            "_id": ObjectId(USUARIO_ID),
            "role": "admin"
        }
        mock_col.delete_one.return_value = MagicMock(deleted_count=0)

        resposta = cliente.delete(
            f'/cidades/{str(ObjectId())}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 404

def test_deletar_cidade_usuario_comum(cliente):
    token = get_token_usuario(cliente)
    with patch('utils_auth.usuarios_collection') as mock_usuarios:
        mock_usuarios.find_one.return_value = {
            "_id": ObjectId(USUARIO_ID),
            "role": "usuario"
        }

        resposta = cliente.delete(
            f'/cidades/{str(CIDADE_MOCK["_id"])}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 403