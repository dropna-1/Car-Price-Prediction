from test.utils import *
from app.main import app
from app.router.user import get_db, get_current_user
from fastapi.testclient import TestClient

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_profile(client, user_test):
    response = client.get("/profile")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("username") == "amir"
    assert response.json().get("balance") == 20000

def test_deposit_balance(client, user_test):
    response = client.patch("/deposit/balance?amount=500")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("balance") == 20500
