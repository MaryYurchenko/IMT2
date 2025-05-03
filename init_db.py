from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db import models


def init_db() -> None:
    db = SessionLocal()

    # Проверяем, существуют ли уже категории
    existing_categories = db.query(models.BMICategory).count()
    if existing_categories == 0:
        # Создаем категории ИМТ
        categories = [
            models.BMICategory(
                name="Недостаточный вес",
                min_value=0,
                max_value=18.5,
                description="Ваш вес ниже нормы",
                recommendations="Рекомендуется увеличить потребление калорий и белка. Проконсультируйтесь с врачом.",
            ),
            models.BMICategory(
                name="Нормальный вес",
                min_value=18.5,
                max_value=25,
                description="У вас нормальный вес",
                recommendations="Поддерживайте текущий образ жизни и питания.",
            ),
            models.BMICategory(
                name="Избыточный вес",
                min_value=25,
                max_value=30,
                description="У вас избыточный вес",
                recommendations="Рекомендуется уменьшить потребление калорий и увеличить физическую активность.",
            ),
            models.BMICategory(
                name="Ожирение",
                min_value=30,
                max_value=float('inf'),
                description="У вас ожирение",
                recommendations="Настоятельно рекомендуется обратиться к врачу для разработки плана по снижению веса.",
            ),
        ]

        db.add_all(categories)
        db.commit()

    db.close()