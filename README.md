# RealEconomy — Backend API

API REST para gerenciamento de imóveis no mercado imobiliário brasileiro. Permite cadastro de usuários, listagem e criação de imóveis, upload de imagens e gerenciamento de cidades.

---

## Sumário

- [Tecnologias](#tecnologias)
- [API Externa — ViaCEP](#api-externa--viacep)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Como Executar](#como-executar)
- [Endpoints](#endpoints)
- [Autenticação](#autenticação)
- [Testes](#testes)

---

## Tecnologias

| Componente       | Tecnologia                    |
|------------------|-------------------------------|
| Linguagem        | Python 3                      |
| Framework        | Flask 3.1.3                   |
| Banco de Dados   | MongoDB (PyMongo 4.17.0)      |
| Autenticação     | JWT (Flask-JWT-Extended 4.7.1)|
| Hash de Senha    | bcrypt 5.0.0                  |
| Upload de Imagens| Cloudinary 1.44.2             |
| CORS             | Flask-CORS 6.0.2              |
| Testes           | pytest 9.0.3 + pytest-flask   |

---

## API Externa — ViaCEP

Este projeto utiliza a **[ViaCEP](https://viacep.com.br/)** — uma API pública e gratuita para consulta de endereços brasileiros a partir do CEP.

**URL base:** `https://viacep.com.br/ws/{cep}/json/`

**Como é utilizada:**

Ao criar ou editar um imóvel, o CEP informado é validado automaticamente pela ViaCEP. A API retorna os dados do logradouro (rua, bairro, cidade, estado) e verifica se o CEP existe e pertence à cidade disponível para cadastro.

**Exemplo de resposta da ViaCEP:**

```json
{
  "cep": "01310-100",
  "logradouro": "Avenida Paulista",
  "bairro": "Bela Vista",
  "localidade": "São Paulo",
  "uf": "SP"
}
```

**Documentação completa:** [https://viacep.com.br/](https://viacep.com.br/)

---

## Configuração do Ambiente

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd 2026-1-progeficaz-projeto3-back-realeconomy
```

### 2. Crie e ative o ambiente virtual

```bash
# Criar
python -m venv .venv

# Ativar — Windows
.venv\Scripts\activate

# Ativar — macOS/Linux
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
MONGO_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/database
JWT_SECRET_KEY=sua_chave_secreta
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret
```

| Variável               | Descrição                              |
|------------------------|----------------------------------------|
| `MONGO_URI`            | String de conexão com o MongoDB Atlas  |
| `JWT_SECRET_KEY`       | Chave para assinar os tokens JWT       |
| `CLOUDINARY_CLOUD_NAME`| Nome do projeto no Cloudinary          |
| `CLOUDINARY_API_KEY`   | Chave pública da API do Cloudinary     |
| `CLOUDINARY_API_SECRET`| Chave secreta da API do Cloudinary     |

---

## Como Executar

```bash
python app.py
```

O servidor inicia em modo de desenvolvimento em `http://localhost:5000`.

---

## Endpoints

### Autenticação — `/auth`

| Método | Rota            | Descrição                                       | Auth |
|--------|-----------------|-------------------------------------------------|------|
| POST   | `/auth/register`| Cadastra novo usuário (valida CPF)              | Não  |
| POST   | `/auth/login`   | Realiza login e retorna tokens JWT              | Não  |
| POST   | `/auth/refresh` | Renova o access token com o refresh token       | Sim  |

---

### Imóveis — `/imoveis`

| Método | Rota              | Descrição                                              | Auth  |
|--------|-------------------|--------------------------------------------------------|-------|
| GET    | `/imoveis`        | Lista todos os imóveis (filtros: cidade, preço, tipo)  | Não   |
| GET    | `/imoveis/<id>`   | Retorna detalhes de um imóvel                          | Não   |
| POST   | `/imoveis`        | Cria novo imóvel (valida CEP via ViaCEP)               | Sim   |
| PUT    | `/imoveis/<id>`   | Edita imóvel (apenas o dono)                           | Sim   |
| DELETE | `/imoveis/<id>`   | Remove imóvel (apenas o dono)                          | Sim   |
| GET    | `/meus-imoveis`   | Lista os imóveis do usuário autenticado                | Sim   |

**Filtros disponíveis em `GET /imoveis`:**

| Parâmetro      | Descrição                              |
|----------------|----------------------------------------|
| `cidade`       | Filtra por cidade                      |
| `preco_min`    | Preço mínimo                           |
| `preco_max`    | Preço máximo                           |
| `tipo`         | Tipo do imóvel (casa, apartamento...)  |
| `tipo_negocio` | Tipo de negócio (venda, aluguel)       |

---

### Cidades — `/cidades`

| Método | Rota              | Descrição                        | Auth        |
|--------|-------------------|----------------------------------|-------------|
| GET    | `/cidades`        | Lista todas as cidades           | Não         |
| POST   | `/cidades`        | Cria nova cidade                 | Admin       |
| DELETE | `/cidades/<id>`   | Remove uma cidade                | Admin       |

---

### Imagens — `/imagens`

| Método | Rota       | Descrição                                       | Auth |
|--------|------------|-------------------------------------------------|------|
| POST   | `/imagens` | Faz upload de imagem para o Cloudinary          | Sim  |

---

## Autenticação

A API usa **JWT (JSON Web Token)** com dois tipos de token:

- **Access Token** — token de curta duração para autenticar requisições
- **Refresh Token** — token de longa duração para renovar o access token

Inclua o access token no cabeçalho das requisições protegidas:

```
Authorization: Bearer <access_token>
```

---

## Testes

Os testes cobrem autenticação, CRUD de imóveis e cidades, permissões e integração com a API ViaCEP.

```bash
# Executar todos os testes
pytest

# Executar com output detalhado
pytest -v

# Executar um arquivo específico
pytest tests/test_auth.py
pytest tests/test_imoveis.py
pytest tests/test_cidades.py
pytest tests/test_api.py
```

| Arquivo de Teste         | Cobertura                                    |
|--------------------------|----------------------------------------------|
| `tests/test_auth.py`     | Registro, login, refresh token, erros        |
| `tests/test_imoveis.py`  | CRUD de imóveis, filtros, permissões         |
| `tests/test_cidades.py`  | CRUD de cidades, controle de acesso admin    |
| `tests/test_api.py`      | Integração com ViaCEP, validação de CEP      |
