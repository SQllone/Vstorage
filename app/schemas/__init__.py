from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, OrderType, OrderStatus
import re


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.worker


class UserCreate(UserBase):
    password: str = Field(
        min_length=6, description="Password must be at least 6 characters long"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str


class UserResponse(User):
    """Response schema for user data"""

    pass


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


# Category schemas
class CategoryBase(BaseModel):
    name: str = Field(min_length=1, description="Category name cannot be empty")
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Category name cannot be empty")
        return v.strip()


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Supplier schemas
class SupplierBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and v.strip():
            # Simple phone validation - should contain only digits, spaces, dashes, parentheses, plus
            phone_pattern = r"^[\+]?[0-9\s\-\(\)]{10,}$"
            if not re.match(phone_pattern, v.strip()):
                raise ValueError("Invalid phone format")
        return v


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class Supplier(SupplierBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str
    category_id: int
    supplier_id: int
    price: float = Field(gt=0, description="Price must be greater than 0")
    quantity_in_stock: int = Field(ge=0, description="Quantity must be non-negative")
    min_stock_level: int = Field(
        ge=0, description="Min stock level must be non-negative"
    )
    unit_of_measure: str = "шт"

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("quantity_in_stock")
    @classmethod
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError("Quantity must be non-negative")
        return v

    @field_validator("min_stock_level")
    @classmethod
    def validate_min_stock(cls, v):
        if v < 0:
            raise ValueError("Min stock level must be non-negative")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    price: Optional[float] = None
    quantity_in_stock: Optional[int] = None
    min_stock_level: Optional[int] = None
    unit_of_measure: Optional[str] = None
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[Category] = None
    supplier: Optional[Supplier] = None

    class Config:
        from_attributes = True


# Order schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    total_price: float

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    order_type: OrderType
    supplier_id: int
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

    @field_validator("items")
    @classmethod
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Order must contain at least one item")
        return v


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None


class Order(OrderBase):
    id: int
    order_number: str
    user_id: int
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    supplier: Optional[Supplier] = None
    items: List[OrderItem] = []

    class Config:
        from_attributes = True


# Response schemas
class ProductWithRelations(Product):
    category_name: Optional[str] = None
    supplier_name: Optional[str] = None


class OrderWithRelations(Order):
    supplier_name: Optional[str] = None
    user_name: Optional[str] = None


class Stats(BaseModel):
    total_products: int
    total_categories: int
    total_suppliers: int
    total_orders: int
    low_stock_products: int
    total_value: float
