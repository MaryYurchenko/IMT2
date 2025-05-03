from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import schemas
from app.api.endpoints.auth import get_current_user
from app.core.security import get_password_hash
from app.db import models
from app.db.session import get_db

router = APIRouter()


@router.post("/", response_model=schemas.User)
def create_user(
        *,
        db: Session = Depends(get_db),
        user_in: schemas.UserCreate,
) -> Any:
    """
    Создание нового пользователя.
    """
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует в системе.",
        )
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует в системе.",
        )

    user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=List[schemas.User])
def read_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Получение списка пользователей.
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.get("/me", response_model=schemas.User)
def read_user_me(
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Получение текущего пользователя.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Получение пользователя по ID.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким ID не существует в системе",
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Обновление данных пользователя.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким ID не существует в системе",
        )

    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Удаление пользователя.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким ID не существует в системе",
        )

    db.delete(user)
    db.commit()
    return user