from test.utils import *
from app.router.auth import get_db, get_current_user

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_user(client):
    user = {
        "username": "saeed",
        "password": "hahahaha"
    }
    response = client.post("/signup", json=user)
    delete_table("users")
    assert response.status_code == status.HTTP_201_CREATED

def test_login_for_access_token(client, user_test):
    user = {
        "username": "amir",
        "password": "12345678"
    }
    response = client.post("/login", data=user)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("token_type") == "bearer"
    assert "access_token" in response.json()

def test_error_login_for_access_token(client, user_test):
    user = {
        "username": "setareh",
        "password": "12345678"
    }
    response = client.post("/login", data=user)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED