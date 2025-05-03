from fastapi import FastAPI
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import auth, users, measurements, bmi
from app.db.base import Base
from app.db.session import engine
from app.db.init_db import init_db

# Создание таблиц базы данных
Base.metadata.create_all(bind=engine)
# Инициализация начальных данных
init_db()

app = FastAPI(title="API для расчёта ИМТ")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(measurements.router, prefix="/measurements", tags=["measurements"])
app.include_router(bmi.router, prefix="/bmi", tags=["bmi"])

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в API для расчёта ИМТ"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)