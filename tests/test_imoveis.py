from unittest.mock import patch, MagicMock
from bson import ObjectId
import bcrypt

CPF_VALIDO_LIMPO = "11144477735"
USUARIO_ID = str(ObjectId())

def get_token(cliente):
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

IMOVEL_MOCK = {
    "_id": ObjectId(),
    "usuario_id": ObjectId(USUARIO_ID),
    "tipo_imovel": "apartamento",
    "tipo_negocio": ["venda"],
    "preco_venda": 350000.0,
    "preco_aluguel": None,
    "cep": "01310100",
    "logradouro": "Avenida Paulista",
    "numero": "1578",
    "complemento": "",
    "bairro": "Bela Vista",
    "cidade": "São Paulo",
    "estado": "SP",
    "descricao": "teste"
}


def test_listar_imoveis(cliente):
    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find.return_value = [IMOVEL_MOCK]

        resposta = cliente.get('/imoveis')
        assert resposta.status_code == 200
        assert len(resposta.get_json()) == 1

def test_buscar_imovel(cliente):
    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find_one.return_value = IMOVEL_MOCK

        resposta = cliente.get(f'/imoveis/{str(IMOVEL_MOCK["_id"])}')
        assert resposta.status_code == 200
        assert resposta.get_json()["tipo_imovel"] == "apartamento"

def test_buscar_imovel_nao_encontrado(cliente):
    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find_one.return_value = None

        resposta = cliente.get(f'/imoveis/{str(ObjectId())}')
        assert resposta.status_code == 404

def test_criar_imovel(cliente):
    token = get_token(cliente)
    with patch('routes.imoveis.imoveis_collection') as mock_imoveis, \
         patch('routes.imoveis.sorteios_collection', create=True), \
         patch('requests.get') as mock_requests:

        mock_requests.return_value.json.return_value = {
            "logradouro": "Avenida Paulista",
            "bairro": "Bela Vista",
            "localidade": "São Paulo",
            "uf": "SP"
        }
        mock_requests.return_value.status_code = 200
        mock_imoveis.insert_one.return_value = MagicMock(inserted_id=ObjectId())

        resposta = cliente.post('/imoveis',
            json={
                "tipo_imovel": "apartamento",
                "tipo_negocio": ["venda"],
                "preco_venda": 350000.0,
                "cep": "01310100",
                "numero": "1578",
                "descricao": "teste"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 201

def test_criar_imovel_sem_token(cliente):
    resposta = cliente.post('/imoveis', json={
        "tipo_imovel": "apartamento",
        "tipo_negocio": ["venda"],
        "preco_venda": 350000.0,
        "cep": "01310100",
        "numero": "1578"
    })
    assert resposta.status_code == 401

def test_deletar_imovel(cliente):
    token = get_token(cliente)
    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find_one.return_value = IMOVEL_MOCK
        mock_col.delete_one.return_value = MagicMock(deleted_count=1)

        resposta = cliente.delete(
            f'/imoveis/{str(IMOVEL_MOCK["_id"])}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 200

def test_deletar_imovel_nao_encontrado(cliente):
    token = get_token(cliente)
    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find_one.return_value = None

        resposta = cliente.delete(
            f'/imoveis/{str(ObjectId())}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 404
        
def test_editar_imovel(cliente):
    token = get_token(cliente)
    with patch('routes.imoveis.imoveis_collection') as mock_col, \
         patch('requests.get') as mock_requests:

        mock_col.find_one.return_value = IMOVEL_MOCK
        mock_col.update_one.return_value = MagicMock()
        mock_col.find_one.side_effect = [
            IMOVEL_MOCK,
            {**IMOVEL_MOCK, "preco_venda": 400000.0}
        ]
        mock_requests.return_value.json.return_value = {
            "logradouro": "Avenida Paulista",
            "bairro": "Bela Vista",
            "localidade": "São Paulo",
            "uf": "SP"
        }

        resposta = cliente.put(
            f'/imoveis/{str(IMOVEL_MOCK["_id"])}',
            json={"preco_venda": 400000.0},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 200

def test_editar_imovel_sem_permissao(cliente):
    token = get_token(cliente)
    outro_usuario_id = str(ObjectId())
    imovel_outro_usuario = {**IMOVEL_MOCK, "usuario_id": ObjectId(outro_usuario_id)}

    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find_one.return_value = imovel_outro_usuario

        resposta = cliente.put(
            f'/imoveis/{str(IMOVEL_MOCK["_id"])}',
            json={"preco_venda": 400000.0},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 403

def test_editar_imovel_nao_encontrado(cliente):
    token = get_token(cliente)
    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find_one.return_value = None

        resposta = cliente.put(
            f'/imoveis/{str(ObjectId())}',
            json={"preco_venda": 400000.0},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 404

def test_deletar_imovel_sem_permissao(cliente):
    token = get_token(cliente)
    outro_usuario_id = str(ObjectId())
    imovel_outro_usuario = {**IMOVEL_MOCK, "usuario_id": ObjectId(outro_usuario_id)}

    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find_one.return_value = imovel_outro_usuario

        resposta = cliente.delete(
            f'/imoveis/{str(IMOVEL_MOCK["_id"])}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 403

def test_meus_imoveis(cliente):
    token = get_token(cliente)
    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find.return_value = [IMOVEL_MOCK]

        resposta = cliente.get(
            '/meus-imoveis',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 200
        assert len(resposta.get_json()) == 1

def test_meus_imoveis_sem_token(cliente):
    resposta = cliente.get('/meus-imoveis')
    assert resposta.status_code == 401

def test_listar_imoveis_filtro_cidade(cliente):
    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find.return_value = [IMOVEL_MOCK]

        resposta = cliente.get('/imoveis?cidade=São Paulo')
        assert resposta.status_code == 200

def test_listar_imoveis_filtro_tipo_negocio(cliente):
    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find.return_value = [IMOVEL_MOCK]

        resposta = cliente.get('/imoveis?tipo_negocio=venda')
        assert resposta.status_code == 200

def test_listar_imoveis_filtro_preco(cliente):
    with patch('routes.imoveis.imoveis_collection') as mock_col:
        mock_col.find.return_value = [IMOVEL_MOCK]

        resposta = cliente.get('/imoveis?preco_min=100000&preco_max=500000')
        assert resposta.status_code == 200