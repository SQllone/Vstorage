from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Category
from app.schemas import Category as CategorySchema, CategoryCreate, CategoryUpdate
from app.auth import get_current_active_user
from app.models import User

router = APIRouter()


@router.get("/", response_model=list[CategorySchema])
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение списка категорий"""
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories


@router.get("/{category_id}", response_model=CategorySchema)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение категории по ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена"
        )
    return category


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Создание новой категории"""
    # Проверяем уникальность названия
    existing_category = (
        db.query(Category).filter(Category.name == category_data.name).first()
    )
    if existing_category:
        raise HTTPException(
            status_code=400, detail="Категория с таким названием уже существует"
        )

    db_category = Category(**category_data.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.patch("/{category_id}", response_model=CategorySchema)
async def patch_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Частичное обновление категории"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена"
        )

    # Проверяем уникальность названия при обновлении
    if category_update.name and category_update.name != category.name:
        existing_category = (
            db.query(Category).filter(Category.name == category_update.name).first()
        )
        if existing_category:
            raise HTTPException(
                status_code=400, detail="Категория с таким названием уже существует"
            )

    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Обновление категории"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена"
        )

    # Проверяем уникальность названия при обновлении
    if category_update.name and category_update.name != category.name:
        existing_category = (
            db.query(Category).filter(Category.name == category_update.name).first()
        )
        if existing_category:
            raise HTTPException(
                status_code=400, detail="Категория с таким названием уже существует"
            )

    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Удаление категории"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена"
        )

    db.delete(category)
    db.commit()
    return {"message": "Категория удалена"}
