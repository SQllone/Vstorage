from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db
from app.models import Order, OrderItem, Product, Supplier, User
from app.schemas import Order as OrderCreate, OrderUpdate, OrderWithRelations, Stats
from app.auth import get_current_active_user
from app.models import Category
from typing import Optional

router = APIRouter()

@router.get("/", response_model=list[OrderWithRelations])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    order_type: Optional[str] = None,
    status: Optional[str] = None,
    supplier_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка заказов с фильтрацией"""
    query = db.query(Order)
    
    # Фильтрация по типу заказа
    if order_type:
        query = query.filter(Order.order_type == order_type)
    
    # Фильтрация по статусу
    if status:
        query = query.filter(Order.status == status)
    
    # Фильтрация по поставщику
    if supplier_id:
        query = query.filter(Order.supplier_id == supplier_id)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    # Добавляем связанные данные
    result = []
    for order in orders:
        # Загружаем позиции для каждого заказа
        order_with_items = db.query(Order).options(
            joinedload(Order.items)
        ).filter(Order.id == order.id).first()
        
        order_dict = {k: v for k, v in order.__dict__.items() if k != 'items'}
        order_data = OrderWithRelations(
            **order_dict,
            supplier_name=order.supplier.name if order.supplier else None,
            user_name=order.user.full_name if order.user else None,
            items=order_with_items.items if order_with_items else []
        )
        result.append(order_data)
    
    return result

@router.get("/{order_id}", response_model=OrderWithRelations)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение заказа по ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    # Загружаем позиции заказа
    order_with_items = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order.id).first()
    
    order_dict = {k: v for k, v in order.__dict__.items() if k != 'items'}
    return OrderWithRelations(
        **order_dict,
        supplier_name=order.supplier.name if order.supplier else None,
        user_name=order.user.full_name if order.user else None,
        items=order_with_items.items if order_with_items else []
    )

@router.post("/", response_model=OrderWithRelations, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание нового заказа"""
    # Проверяем существование поставщика
    supplier = db.query(Supplier).filter(Supplier.id == order_data.supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=400,
            detail="Указанный поставщик не найден"
        )
    
    # Генерируем номер заказа
    last_order = db.query(Order).order_by(Order.id.desc()).first()
    order_number = f"ORD-{last_order.id + 1:06d}" if last_order else "ORD-000001"
    
    # Создаем заказ
    db_order = Order(
        order_number=order_number,
        order_type=order_data.order_type,
        supplier_id=order_data.supplier_id,
        user_id=current_user.id,
        notes=order_data.notes
    )
    db.add(db_order)
    db.flush()  # Получаем ID заказа
    
    total_amount = 0
    
    # Добавляем позиции заказа
    for item_data in order_data.items:
        # Проверяем существование товара
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=400,
                detail=f"Товар с ID {item_data.product_id} не найден"
            )
        
        # Вычисляем общую стоимость позиции
        total_price = item_data.quantity * item_data.unit_price
        total_amount += total_price
        
        # Создаем позицию заказа
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=total_price
        )
        db.add(db_item)
        
        # Обновляем остаток товара
        if order_data.order_type == "supply":
            # Приход - увеличиваем остаток
            product.quantity_in_stock += item_data.quantity
        elif order_data.order_type == "shipment":
            # Расход - уменьшаем остаток
            if product.quantity_in_stock < item_data.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Недостаточно товара {product.name} на складе"
                )
            product.quantity_in_stock -= item_data.quantity
    
    # Обновляем общую сумму заказа
    db_order.total_amount = total_amount
    
    db.commit()
    db.refresh(db_order)
    
    # Загружаем заказ с позициями
    db_order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == db_order.id).first()
    
    # Подготавливаем данные для ответа
    order_dict = {k: v for k, v in db_order.__dict__.items() if k != 'items'}
    return OrderWithRelations(
        **order_dict,
        supplier_name=supplier.name,
        user_name=current_user.full_name,
        items=db_order.items
    )

@router.put("/{order_id}", response_model=OrderWithRelations)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновление заказа"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    # Загружаем заказ с позициями
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order.id).first()
    
    # Подготавливаем данные для ответа
    order_dict = {k: v for k, v in order.__dict__.items() if k != 'items'}
    return OrderWithRelations(
        **order_dict,
        supplier_name=order.supplier.name if order.supplier else None,
        user_name=order.user.full_name if order.user else None,
        items=order.items
    )

@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удаление заказа"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    db.delete(order)
    db.commit()
    return {"message": "Заказ удален"}

@router.get("/stats/overview", response_model=Stats)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение общей статистики"""
    # Подсчитываем общее количество товаров
    total_products = db.query(func.count(Product.id)).filter(Product.is_active).scalar()
    
    # Подсчитываем количество категорий
    total_categories = db.query(func.count(Category.id)).scalar()
    
    # Подсчитываем количество поставщиков
    total_suppliers = db.query(func.count(Supplier.id)).scalar()
    
    # Подсчитываем количество заказов
    total_orders = db.query(func.count(Order.id)).scalar()
    
    # Подсчитываем товары с низким остатком
    low_stock_products = db.query(func.count(Product.id)).filter(
        Product.is_active,
        Product.quantity_in_stock <= Product.min_stock_level
    ).scalar()
    
    # Подсчитываем общую стоимость товаров на складе
    total_value = db.query(func.sum(Product.quantity_in_stock * Product.price)).filter(
        Product.is_active
    ).scalar() or 0
    
    return Stats(
        total_products=total_products,
        total_categories=total_categories,
        total_suppliers=total_suppliers,
        total_orders=total_orders,
        low_stock_products=low_stock_products,
        total_value=total_value
    )