import pytest
from app import app


@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "test_secret"
    with app.test_client() as cliente:
        yield cliente
        