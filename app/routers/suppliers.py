from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Supplier
from app.schemas import Supplier as SupplierSchema, SupplierCreate, SupplierUpdate
from app.auth import get_current_active_user
from app.models import User

router = APIRouter()


@router.get("/", response_model=list[SupplierSchema])
async def get_suppliers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение списка поставщиков"""
    suppliers = db.query(Supplier).offset(skip).limit(limit).all()
    return suppliers


@router.get("/{supplier_id}", response_model=SupplierSchema)
async def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение поставщика по ID"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Поставщик не найден"
        )
    return supplier


@router.post("/", response_model=SupplierSchema, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Создание нового поставщика"""
    # Проверяем уникальность названия
    existing_supplier = (
        db.query(Supplier).filter(Supplier.name == supplier_data.name).first()
    )
    if existing_supplier:
        raise HTTPException(
            status_code=400, detail="Поставщик с таким названием уже существует"
        )

    db_supplier = Supplier(**supplier_data.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


@router.put("/{supplier_id}", response_model=SupplierSchema)
async def update_supplier(
    supplier_id: int,
    supplier_update: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Обновление поставщика"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Поставщик не найден"
        )

    # Проверяем уникальность названия при обновлении
    if supplier_update.name and supplier_update.name != supplier.name:
        existing_supplier = (
            db.query(Supplier).filter(Supplier.name == supplier_update.name).first()
        )
        if existing_supplier:
            raise HTTPException(
                status_code=400, detail="Поставщик с таким названием уже существует"
            )

    update_data = supplier_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Удаление поставщика"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Поставщик не найден"
        )

    db.delete(supplier)
    db.commit()
    return {"message": "Поставщик удален"}
