from test.utils import *
from app.router.admin import get_db, get_current_user

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_list_users(client, user_test):
    response = client.get("admin/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0].get("id") == 1
    assert response.json()[0].get("username") == "amir"

def test_list_admins(client, db):
    user = User(id=1, username="amir",
                hashed_password=bcrypt_context.hash("12345678"), role="admin")
    db.add(user)
    db.commit()
    response = client.get("admin/admins")
    delete_table("users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0].get("id") == 1
    assert response.json()[0].get("username") == "amir"

def test_empty_list_admins(client, user_test):
    response = client.get("admin/admins")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0

def test_add_admin(client, user_test):
    response = client.patch("admin/add?user_id=1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == "user promoted"

def test_delete_user(client, user_test, db):
    response = client.delete("admin/del_user/1")
    user = db.query(User).filter(User.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert user is None

def test_delete_car(client, user_test, car_test, db):
    response = client.delete("admin/del_car/1")
    car = db.query(Car).filter(Car.id == 1).first()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert car is None
