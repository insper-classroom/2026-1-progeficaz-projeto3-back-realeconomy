from unittest.mock import patch, MagicMock
from bson import ObjectId
import bcrypt

USUARIO_ID = str(ObjectId())
CPF_VALIDO_LIMPO = "11144477735"

ENDERECO_MOCK = {
    "logradouro": "Avenida Paulista",
    "bairro": "Bela Vista",
    "localidade": "São Paulo",
    "uf": "SP"
}

IMOVEL_BASE = {
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


def get_token(cliente):
    senha_hash = bcrypt.hashpw("123456".encode("utf-8"), bcrypt.gensalt())
    with patch("routes.auth.usuarios_collection") as mock_col:
        mock_col.find_one.return_value = {
            "_id": ObjectId(USUARIO_ID),
            "nome": "Teste",
            "cpf": CPF_VALIDO_LIMPO,
            "senha": senha_hash,
            "role": "usuario"
        }
        resposta = cliente.post("/auth/login", json={"cpf": CPF_VALIDO_LIMPO, "senha": "123456"})
        return resposta.get_json()["access_token"]


# --- POST /imoveis: criação com CEP ---

def test_criar_imovel_cep_valido(cliente):
    token = get_token(cliente)
    with patch("routes.imoveis.imoveis_collection") as mock_col, \
         patch("requests.get") as mock_get:

        mock_get.return_value.json.return_value = ENDERECO_MOCK
        mock_col.insert_one.return_value = MagicMock(inserted_id=ObjectId())

        resposta = cliente.post(
            "/imoveis",
            json={
                "tipo_imovel": "apartamento",
                "tipo_negocio": ["venda"],
                "preco_venda": 350000.0,
                "cep": "01310100",
                "numero": "1578",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 201
        mock_get.assert_called_once_with("https://viacep.com.br/ws/01310100/json/")


def test_criar_imovel_cep_com_hifen(cliente):
    """CEP formatado com hífen deve ser limpo antes de consultar a API."""
    token = get_token(cliente)
    with patch("routes.imoveis.imoveis_collection") as mock_col, \
         patch("requests.get") as mock_get:

        mock_get.return_value.json.return_value = ENDERECO_MOCK
        mock_col.insert_one.return_value = MagicMock(inserted_id=ObjectId())

        cliente.post(
            "/imoveis",
            json={
                "tipo_imovel": "apartamento",
                "tipo_negocio": ["venda"],
                "preco_venda": 350000.0,
                "cep": "01310-100",
                "numero": "1578",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        mock_get.assert_called_once_with("https://viacep.com.br/ws/01310100/json/")


def test_criar_imovel_cep_inexistente(cliente):
    """ViaCEP retorna {"erro": true} para CEPs inválidos → 400."""
    token = get_token(cliente)
    with patch("routes.imoveis.imoveis_collection"), \
         patch("requests.get") as mock_get:

        mock_get.return_value.json.return_value = {"erro": True}

        resposta = cliente.post(
            "/imoveis",
            json={
                "tipo_imovel": "apartamento",
                "tipo_negocio": ["venda"],
                "preco_venda": 350000.0,
                "cep": "00000000",
                "numero": "1",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 400
        assert "CEP não encontrado" in resposta.get_json()["erro"]


def test_criar_imovel_cep_falha_de_rede(cliente):
    """Exceção ao chamar ViaCEP → 500."""
    token = get_token(cliente)
    with patch("routes.imoveis.imoveis_collection"), \
         patch("requests.get") as mock_get:

        mock_get.side_effect = Exception("timeout")

        resposta = cliente.post(
            "/imoveis",
            json={
                "tipo_imovel": "apartamento",
                "tipo_negocio": ["venda"],
                "preco_venda": 350000.0,
                "cep": "01310100",
                "numero": "1578",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 500
        assert "Erro ao consultar CEP" in resposta.get_json()["erro"]


# --- PUT /imoveis/<id>: edição com CEP ---

def test_editar_imovel_cep_valido(cliente):
    token = get_token(cliente)
    imovel_atualizado = {**IMOVEL_BASE, "cep": "04538133"}

    with patch("routes.imoveis.imoveis_collection") as mock_col, \
         patch("requests.get") as mock_get:

        mock_col.find_one.side_effect = [IMOVEL_BASE, imovel_atualizado]
        mock_col.update_one.return_value = MagicMock()
        mock_get.return_value.json.return_value = {
            "logradouro": "Rua Funchal",
            "bairro": "Vila Olímpia",
            "localidade": "São Paulo",
            "uf": "SP"
        }

        resposta = cliente.put(
            f"/imoveis/{str(IMOVEL_BASE['_id'])}",
            json={"cep": "04538133"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 200
        mock_get.assert_called_once_with("https://viacep.com.br/ws/04538133/json/")


def test_editar_imovel_cep_com_hifen(cliente):
    """CEP com hífen no PUT também deve ser limpo."""
    token = get_token(cliente)
    imovel_atualizado = {**IMOVEL_BASE, "cep": "04538133"}

    with patch("routes.imoveis.imoveis_collection") as mock_col, \
         patch("requests.get") as mock_get:

        mock_col.find_one.side_effect = [IMOVEL_BASE, imovel_atualizado]
        mock_col.update_one.return_value = MagicMock()
        mock_get.return_value.json.return_value = {
            "logradouro": "Rua Funchal",
            "bairro": "Vila Olímpia",
            "localidade": "São Paulo",
            "uf": "SP"
        }

        cliente.put(
            f"/imoveis/{str(IMOVEL_BASE['_id'])}",
            json={"cep": "04538-133"},
            headers={"Authorization": f"Bearer {token}"}
        )
        mock_get.assert_called_once_with("https://viacep.com.br/ws/04538133/json/")


def test_editar_imovel_cep_inexistente(cliente):
    token = get_token(cliente)
    with patch("routes.imoveis.imoveis_collection") as mock_col, \
         patch("requests.get") as mock_get:

        mock_col.find_one.return_value = IMOVEL_BASE
        mock_get.return_value.json.return_value = {"erro": True}

        resposta = cliente.put(
            f"/imoveis/{str(IMOVEL_BASE['_id'])}",
            json={"cep": "00000000"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 400
        assert "CEP não encontrado" in resposta.get_json()["erro"]


def test_editar_imovel_cep_falha_de_rede(cliente):
    token = get_token(cliente)
    with patch("routes.imoveis.imoveis_collection") as mock_col, \
         patch("requests.get") as mock_get:

        mock_col.find_one.return_value = IMOVEL_BASE
        mock_get.side_effect = Exception("connection refused")

        resposta = cliente.put(
            f"/imoveis/{str(IMOVEL_BASE['_id'])}",
            json={"cep": "01310100"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 500
        assert "Erro ao consultar CEP" in resposta.get_json()["erro"]


def test_editar_imovel_sem_cep_nao_consulta_api(cliente):
    """PUT sem campo 'cep' não deve chamar a API ViaCEP."""
    token = get_token(cliente)
    imovel_atualizado = {**IMOVEL_BASE, "preco_venda": 400000.0}

    with patch("routes.imoveis.imoveis_collection") as mock_col, \
         patch("requests.get") as mock_get:

        mock_col.find_one.side_effect = [IMOVEL_BASE, imovel_atualizado]
        mock_col.update_one.return_value = MagicMock()

        resposta = cliente.put(
            f"/imoveis/{str(IMOVEL_BASE['_id'])}",
            json={"preco_venda": 400000.0},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resposta.status_code == 200
        mock_get.assert_not_called()
