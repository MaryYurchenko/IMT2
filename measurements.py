from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.api.endpoints.auth import get_current_user
from app.db import models
from app.db.session import get_db

router = APIRouter()


@router.post("/", response_model=schemas.Measurement)
def create_measurement(
        *,
        db: Session = Depends(get_db),
        measurement_in: schemas.MeasurementCreate,
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Создание нового измерения.
    """
    measurement = models.Measurement(
        **measurement_in.dict(),
        user_id=current_user.id,
    )
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return measurement


@router.get("/", response_model=List[schemas.Measurement])
def read_measurements(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Получение списка измерений пользователя.
    """
    measurements = (
        db.query(models.Measurement)
        .filter(models.Measurement.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return measurements


@router.get("/{measurement_id}", response_model=schemas.Measurement)
def read_measurement(
        *,
        db: Session = Depends(get_db),
        measurement_id: int,
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Получение измерения по ID.
    """
    measurement = db.query(models.Measurement).filter(
        models.Measurement.id == measurement_id,
        models.Measurement.user_id == current_user.id,
    ).first()
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Измерение с этим ID не существует в системе",
        )
    return measurement


@router.put("/{measurement_id}", response_model=schemas.Measurement)
def update_measurement(
        *,
        db: Session = Depends(get_db),
        measurement_id: int,
        measurement_in: schemas.MeasurementUpdate,
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Обновление измерения.
    """
    measurement = db.query(models.Measurement).filter(
        models.Measurement.id == measurement_id,
        models.Measurement.user_id == current_user.id,
    ).first()
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Измерение с этим ID не существует в системе",
        )

    update_data = measurement_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(measurement, field, update_data[field])

    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return measurement


@router.delete("/{measurement_id}", response_model=schemas.Measurement)
def delete_measurement(
        *,
        db: Session = Depends(get_db),
        measurement_id: int,
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Удаление измерения.
    """
    measurement = db.query(models.Measurement).filter(
        models.Measurement.id == measurement_id,
        models.Measurement.user_id == current_user.id,
    ).first()
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Измерение с этим ID не существует в системе",
        )

    db.delete(measurement)
    db.commit()
    return measurement