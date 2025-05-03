from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.main import app
from app.db.session import get_db
from app.db.init_db import init_db

# Настройка тестовой базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание и инициализация базы данных для тестов
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
init_db()

client = TestClient(app)


def test_calculate_bmi():
    # Сначала регистрируем пользователя
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 200

    # Логинимся для получения токена
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword",
        },
    )
    assert response.status_code == 200
    token_data = response.json()
    token = token_data["access_token"]

    # Рассчитываем ИМТ
    response = client.post(
        "/bmi/calculate",
        json={
            "weight": 70.0,
            "height": 175.0,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    bmi_data = response.json()
    assert "bmi" in bmi_data
    assert "category" in bmi_data
    assert "description" in bmi_data
    assert "recommendations" in bmi_data

    # Проверяем правильность расчета ИМТ
    height_m = 175.0 / 100
    expected_bmi = 70.0 / (height_m ** 2)
    assert abs(bmi_data["bmi"] - round(expected_bmi, 2)) < 0.1  # Допускаем небольшую погрешность из-за округления