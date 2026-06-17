from test.utils import *
from app.router.car import get_db, get_current_user

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_list_cars(client, user_test, car_test):
    response = client.get("car/list")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0].get("id") == 1
    assert response.json()[0].get("Mileage") == 10
    assert response.json()[0].get("Type") == "Sedan"
    assert response.json()[0].get("Cylinder") == 6

def test_delete_car_by_id(client, user_test, car_test, db):
    response = client.delete("car/del/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db.query(Car).count() == 0

def test_error_delete_car_by_id(client, user_test, car_test, db):
    response = client.delete("car/del/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert db.query(Car).count() == 1

def test_add_car(client, user_test):
    car = {
        "Mileage": 16229, "Type": "Sedan", "Cylinder": 6,
        "Liter": 3, "Doors": 4, "Cruise": 1,
        "Sound": 0, "Leather": 0
    }
    response = client.post("car", json=car)
    delete_table("cars")
    assert response.status_code == status.HTTP_201_CREATED
    assert int(response.json().get("Price")) == 16855

def test_sale_car(client, user_test, car_test, db):
    user = User(id=2, username="nima", hashed_password="87654321")
    car = Car(id=2, Mileage=10, Type="Sedan", Cylinder=6, Liter=1,
              Doors=4, Sound=0, Leather=1, Cruise=1, Price=16655, owner_id=2)
    db.add(user)
    db.commit()
    db.add(car)
    db.commit()
    current_user = db.query(User).filter(User.id == 1).first()
    seller_user = db.query(User).filter(User.id == 2).first()
    car = db.query(Car).filter(Car.id == 2).first()
    response = client.post("car/sale?car_id=2")
    assert response.status_code == status.HTTP_201_CREATED
    assert current_user.balance == 20000 - 16655
    assert seller_user.balance == 16655
    assert car.is_sale == True
    assert car.owner_id == 1

def test_forbidden_sale_car(client, user_test, car_test, db):
    response = client.post("car/sale?car_id=1")
    assert response.status_code == status.HTTP_403_FORBIDDEN
