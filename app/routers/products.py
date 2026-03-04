from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.database import get_db
from app.models import Product, Category, Supplier
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductWithRelations,
)
from app.auth import get_current_active_user
from app.models import User
from typing import Optional

router = APIRouter()


@router.get("/", response_model=list[ProductWithRelations])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    low_stock: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение списка товаров с фильтрацией"""
    query = db.query(Product).filter(Product.is_active)

    # Фильтрация по категории
    if category_id:
        query = query.filter(Product.category_id == category_id)

    # Фильтрация по поставщику
    if supplier_id:
        query = query.filter(Product.supplier_id == supplier_id)

    # Фильтрация по низкому остатку
    if low_stock:
        query = query.filter(Product.quantity_in_stock <= Product.min_stock_level)

    # Поиск по названию, SKU или описанию
    if search:
        search_filter = or_(
            Product.name.contains(search),
            Product.sku.contains(search),
            Product.description.contains(search),
        )
        query = query.filter(search_filter)

    products = query.offset(skip).limit(limit).all()

    # Добавляем связанные данные
    result = []
    for product in products:
        product_data = ProductWithRelations(
            **product.__dict__,
            category_name=product.category.name if product.category else None,
            supplier_name=product.supplier.name if product.supplier else None,
        )
        result.append(product_data)

    return result


@router.get("/{product_id}", response_model=ProductWithRelations)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение товара по ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден"
        )

    return ProductWithRelations(
        **product.__dict__,
        category_name=product.category.name if product.category else None,
        supplier_name=product.supplier.name if product.supplier else None,
    )


@router.post(
    "/", response_model=ProductWithRelations, status_code=status.HTTP_201_CREATED
)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Создание нового товара"""
    # Проверяем уникальность SKU
    existing_product = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Товар с таким SKU уже существует")

    # Проверяем существование категории
    category = (
        db.query(Category).filter(Category.id == product_data.category_id).first()
    )
    if not category:
        raise HTTPException(status_code=400, detail="Указанная категория не найдена")

    # Проверяем существование поставщика
    supplier = (
        db.query(Supplier).filter(Supplier.id == product_data.supplier_id).first()
    )
    if not supplier:
        raise HTTPException(status_code=400, detail="Указанный поставщик не найден")

    # Создаем товар
    db_product = Product(**product_data.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Загружаем связанные данные с join
    db_product = (
        db.query(Product)
        .options(joinedload(Product.category), joinedload(Product.supplier))
        .filter(Product.id == db_product.id)
        .first()
    )

    return ProductWithRelations(
        **db_product.__dict__,
        category_name=db_product.category.name if db_product.category else None,
        supplier_name=db_product.supplier.name if db_product.supplier else None,
    )


@router.put("/{product_id}", response_model=ProductWithRelations)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Обновление товара"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден"
        )

    # Проверяем уникальность SKU при обновлении
    if product_update.sku and product_update.sku != product.sku:
        existing_product = (
            db.query(Product).filter(Product.sku == product_update.sku).first()
        )
        if existing_product:
            raise HTTPException(
                status_code=400, detail="Товар с таким SKU уже существует"
            )

    # Проверяем существование категории при обновлении
    if product_update.category_id:
        category = (
            db.query(Category).filter(Category.id == product_update.category_id).first()
        )
        if not category:
            raise HTTPException(
                status_code=400, detail="Указанная категория не найдена"
            )

    # Проверяем существование поставщика при обновлении
    if product_update.supplier_id:
        supplier = (
            db.query(Supplier).filter(Supplier.id == product_update.supplier_id).first()
        )
        if not supplier:
            raise HTTPException(status_code=400, detail="Указанный поставщик не найден")

    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return ProductWithRelations(
        **product.__dict__,
        category_name=product.category.name if product.category else None,
        supplier_name=product.supplier.name if product.supplier else None,
    )


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Удаление товара (помечаем как неактивный)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден"
        )

    product.is_active = False
    db.commit()

    return {"message": "Товар помечен как удаленный"}


@router.get("/low-stock/list", response_model=list[ProductWithRelations])
async def get_low_stock_products(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Получение товаров с низким остатком"""
    products = (
        db.query(Product)
        .filter(
            Product.is_active,
            Product.quantity_in_stock <= Product.min_stock_level,
        )
        .all()
    )

    result = []
    for product in products:
        product_data = ProductWithRelations(
            **product.__dict__,
            category_name=product.category.name if product.category else None,
            supplier_name=product.supplier.name if product.supplier else None,
        )
        result.append(product_data)

    return result
