#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Pydantic schemas validation
Testing data validation logic in isolation
"""

import pytest
from pydantic import ValidationError
from app.schemas import (
    UserCreate,
    ProductCreate,
    CategoryCreate,
    SupplierCreate,
    OrderCreate,
)


class TestUserCreateValidation:
    """Test UserCreate schema validation"""

    def test_valid_user_data(self):
        """Test valid user creation data"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpass123",
        }
        user = UserCreate(**data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "testpass123"

    def test_invalid_email_format(self):
        """Test invalid email format"""
        data = {
            "username": "testuser",
            "email": "invalid-email",
            "full_name": "Test User",
            "password": "testpass123",
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_password_too_short(self):
        """Test password length validation"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "123",
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_missing_required_field(self):
        """Test missing required field"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)


class TestProductCreateValidation:
    """Test ProductCreate schema validation"""

    def test_valid_product_data(self):
        """Test valid product creation data"""
        data = {
            "name": "Test Product",
            "description": "Test product description",
            "sku": "TEST-001",
            "category_id": 1,
            "supplier_id": 1,
            "price": 99.99,
            "quantity_in_stock": 10,
            "min_stock_level": 2,
            "unit_of_measure": "шт",
        }
        product = ProductCreate(**data)
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert product.quantity_in_stock == 10

    def test_negative_price(self):
        """Test negative price validation"""
        data = {
            "name": "Test Product",
            "description": "Test product description",
            "sku": "TEST-001",
            "category_id": 1,
            "supplier_id": 1,
            "price": -99.99,
            "quantity_in_stock": 10,
            "min_stock_level": 2,
            "unit_of_measure": "шт",
        }
        with pytest.raises(ValidationError):
            ProductCreate(**data)

    def test_negative_quantity(self):
        """Test negative stock quantity validation"""
        data = {
            "name": "Test Product",
            "description": "Test product description",
            "sku": "TEST-001",
            "category_id": 1,
            "supplier_id": 1,
            "price": 99.99,
            "quantity_in_stock": -10,
            "min_stock_level": 2,
            "unit_of_measure": "шт",
        }
        with pytest.raises(ValidationError):
            ProductCreate(**data)

    def test_zero_price(self):
        """Test zero price validation"""
        data = {
            "name": "Test Product",
            "description": "Test product description",
            "sku": "TEST-001",
            "category_id": 1,
            "supplier_id": 1,
            "price": 0,
            "quantity_in_stock": 10,
            "min_stock_level": 2,
            "unit_of_measure": "шт",
        }
        with pytest.raises(ValidationError):
            ProductCreate(**data)


class TestCategoryCreateValidation:
    """Test CategoryCreate schema validation"""

    def test_valid_category_data(self):
        """Test valid category creation data"""
        data = {"name": "Electronics", "description": "Electronic devices"}
        category = CategoryCreate(**data)
        assert category.name == "Electronics"
        assert category.description == "Electronic devices"

    def test_empty_category_name(self):
        """Test empty category name validation"""
        data = {"name": "", "description": "Electronic devices"}
        with pytest.raises(ValidationError):
            CategoryCreate(**data)

    def test_whitespace_only_name(self):
        """Test whitespace-only category name"""
        data = {"name": "   ", "description": "Electronic devices"}
        with pytest.raises(ValidationError):
            CategoryCreate(**data)

    def test_missing_category_name(self):
        """Test missing category name"""
        data = {"description": "Electronic devices"}
        with pytest.raises(ValidationError):
            CategoryCreate(**data)


class TestSupplierCreateValidation:
    """Test SupplierCreate schema validation"""

    def test_valid_supplier_data(self):
        """Test valid supplier creation data"""
        data = {
            "name": "Test Supplier LLC",
            "contact_person": "John Doe",
            "phone": "+7-495-123-45-67",
            "email": "supplier@example.com",
            "address": "123 Test Street",
        }
        supplier = SupplierCreate(**data)
        assert supplier.name == "Test Supplier LLC"
        assert supplier.email == "supplier@example.com"

    def test_invalid_phone_format(self):
        """Test invalid phone format validation"""
        data = {
            "name": "Test Supplier LLC",
            "contact_person": "John Doe",
            "phone": "invalid-phone",
            "email": "supplier@example.com",
            "address": "123 Test Street",
        }
        with pytest.raises(ValidationError):
            SupplierCreate(**data)

    def test_optional_phone_field(self):
        """Test optional phone field"""
        data = {
            "name": "Test Supplier LLC",
            "contact_person": "John Doe",
            "phone": None,
            "email": "supplier@example.com",
            "address": "123 Test Street",
        }
        supplier = SupplierCreate(**data)
        assert supplier.phone is None

    def test_valid_phone_variants(self):
        """Test valid phone number variants"""
        valid_phones = [
            "+7-495-123-45-67",
            "+7 (495) 123-45-67",
            "7 495 1234567",
            "+79991234567",
        ]
        for phone in valid_phones:
            data = {
                "name": "Test Supplier LLC",
                "contact_person": "John Doe",
                "phone": phone,
                "email": "supplier@example.com",
                "address": "123 Test Street",
            }
            supplier = SupplierCreate(**data)
            assert supplier.phone == phone


class TestOrderCreateValidation:
    """Test OrderCreate schema validation"""

    def test_valid_order_data(self):
        """Test valid order creation data"""
        data = {
            "order_type": "supply",
            "supplier_id": 1,
            "notes": "Test order notes",
            "items": [{"product_id": 1, "quantity": 5, "unit_price": 99.99}],
        }
        order = OrderCreate(**data)
        assert order.order_type == "supply"
        assert len(order.items) == 1
        assert order.items[0].quantity == 5

    def test_invalid_order_type(self):
        """Test invalid order type validation"""
        data = {
            "order_type": "invalid_type",
            "supplier_id": 1,
            "notes": "Test order notes",
            "items": [{"product_id": 1, "quantity": 5, "unit_price": 99.99}],
        }
        with pytest.raises(ValidationError):
            OrderCreate(**data)

    def test_empty_items_list(self):
        """Test empty order items validation"""
        data = {
            "order_type": "supply",
            "supplier_id": 1,
            "notes": "Test order notes",
            "items": [],
        }
        with pytest.raises(ValidationError):
            OrderCreate(**data)

    def test_valid_order_types(self):
        """Test valid order types"""
        valid_types = ["supply", "shipment"]
        for order_type in valid_types:
            data = {
                "order_type": order_type,
                "supplier_id": 1,
                "notes": "Test order notes",
                "items": [{"product_id": 1, "quantity": 5, "unit_price": 99.99}],
            }
            order = OrderCreate(**data)
            assert order.order_type == order_type
