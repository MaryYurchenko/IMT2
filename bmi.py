from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.api.endpoints.auth import get_current_user
from app.db import models
from app.db.session import get_db

router = APIRouter()


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Расчет индекса массы тела (ИМТ)
    Формула: вес (кг) / (рост (м))^2
    """
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


@router.post("/calculate", response_model=schemas.BMIResult)
def calculate_bmi_endpoint(
        *,
        db: Session = Depends(get_db),
        bmi_in: schemas.BMICalculate,
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Расчёт ИМТ и возврат результата с информацией о категории.
    """
    bmi_value = calculate_bmi(bmi_in.weight, bmi_in.height)

    # Находим соответствующую категорию ИМТ
    bmi_category = db.query(models.BMICategory).filter(
        models.BMICategory.min_value <= bmi_value,
        models.BMICategory.max_value > bmi_value,
    ).first()

    if not bmi_category:
        # Если категория не найдена, берем самую высокую для очень больших значений ИМТ
        bmi_category = db.query(models.BMICategory).order_by(
            models.BMICategory.max_value.desc()
        ).first()

    # Сохраняем измерение
    measurement = models.Measurement(
        user_id=current_user.id,
        weight=bmi_in.weight,
        height=bmi_in.height,
    )
    db.add(measurement)
    db.commit()

    return {
        "bmi": round(bmi_value, 2),
        "category": bmi_category.name,
        "description": bmi_category.description,
        "recommendations": bmi_category.recommendations,
    }


@router.post("/categories", response_model=schemas.BMICategory)
def create_bmi_category(
        *,
        db: Session = Depends(get_db),
        category_in: schemas.BMICategoryCreate,
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Создание новой категории ИМТ.
    """
    category = models.BMICategory(**category_in.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories/{category_id}", response_model=schemas.BMICategory)
def read_bmi_category(
        *,
        db: Session = Depends(get_db),
        category_id: int,
) -> Any:
    """
    Получение категории ИМТ по ID.
    """
    category = db.query(models.BMICategory).filter(models.BMICategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория ИМТ с этим ID не существует в системе",
        )
    return category