from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, User as UserSchema, Token, UserLogin
from app.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    verify_token,
    get_current_user,
)
from app.rate_limiter import limiter

# Проверка на тестовый режим
TESTING_MODE = os.getenv("TESTING", "false").lower() == "true"

router = APIRouter()


@router.post(
    "/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
@limiter.limit(
    "3/minute", exempt_when=lambda: TESTING_MODE
)  # Ограничение: 3 запроса в минуту
async def register_user(
    user_data: UserCreate, request: Request, db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    # Проверяем, существует ли пользователь с таким именем
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Пользователь с таким именем уже существует"
        )

    # Проверяем, существует ли пользователь с таким email
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует"
        )

    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
@limiter.limit(
    "5/minute", exempt_when=lambda: TESTING_MODE
)  # Ограничение: 5 запросов в минуту
async def login_user(
    login_data: UserLogin, request: Request, db: Session = Depends(get_db)
):
    """Вход пользователя в систему"""
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """Выход пользователя (для демонстрации)"""
    return {"message": "Пользователь успешно вышел из системы"}


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user


@router.get("/verify-token")
async def verify_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    """Проверка валидности токена"""
    try:
        # Проверяем токен через зависимость
        token_data = verify_token(credentials)
        return {"valid": True, "username": token_data["username"]}
    except HTTPException:
        return {"valid": False, "detail": "Недействительный токен"}
