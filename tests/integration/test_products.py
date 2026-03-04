#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for products endpoints
Testing CRUD operations for products
"""

from fastapi import status


class TestProductCRUD:
    """Test product CRUD operations"""

    def test_create_product(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test creating a product"""
        # Create category
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        # Create supplier
        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        # Create product
        product_data = {
            "name": "Test Laptop",
            "description": "High-performance laptop",
            "sku": "LAPTOP-001",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": 1299.99,
            "quantity_in_stock": 5,
            "min_stock_level": 1,
            "unit_of_measure": "шт",
        }
        response = client.post("/products/", json=product_data, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == product_data["name"]
        assert data["price"] == product_data["price"]
        assert "id" in data

    def test_get_products(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test getting list of products"""
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        product_data = {
            "name": "Test Mouse",
            "description": "Wireless mouse",
            "sku": "MOUSE-001",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": 29.99,
            "quantity_in_stock": 50,
            "min_stock_level": 5,
            "unit_of_measure": "шт",
        }
        client.post("/products/", json=product_data, headers=auth_headers)

        response = client.get("/products/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        products = response.json()
        assert len(products) >= 1

    def test_get_product_by_id(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test getting single product by ID"""
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        product_data = {
            "name": "Test Keyboard",
            "description": "Mechanical keyboard",
            "sku": "KEYBOARD-001",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": 89.99,
            "quantity_in_stock": 20,
            "min_stock_level": 2,
            "unit_of_measure": "шт",
        }
        create_response = client.post(
            "/products/", json=product_data, headers=auth_headers
        )
        product_id = create_response.json()["id"]

        response = client.get(f"/products/{product_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == product_data["name"]

    def test_update_product(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test updating a product"""
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        product_data = {
            "name": "Test Monitor",
            "description": "4K monitor",
            "sku": "MONITOR-001",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": 399.99,
            "quantity_in_stock": 10,
            "min_stock_level": 1,
            "unit_of_measure": "шт",
        }
        create_response = client.post(
            "/products/", json=product_data, headers=auth_headers
        )
        product_id = create_response.json()["id"]

        update_data = {"price": 349.99}
        response = client.put(
            f"/products/{product_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["price"] == 349.99

    def test_delete_product(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test deleting a product"""
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        product_data = {
            "name": "Test Headphones",
            "description": "Wireless headphones",
            "sku": "HEADPHONES-001",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": 149.99,
            "quantity_in_stock": 15,
            "min_stock_level": 2,
            "unit_of_measure": "шт",
        }
        create_response = client.post(
            "/products/", json=product_data, headers=auth_headers
        )
        product_id = create_response.json()["id"]

        response = client.delete(f"/products/{product_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_create_product_invalid_price(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test creating product with invalid price"""
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        product_data = {
            "name": "Invalid Product",
            "description": "Test",
            "sku": "INVALID-001",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": -99.99,
            "quantity_in_stock": 10,
            "min_stock_level": 2,
            "unit_of_measure": "шт",
        }
        response = client.post("/products/", json=product_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_low_stock_products(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test getting low stock products"""
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        product_data = {
            "name": "Low Stock Product",
            "description": "Test",
            "sku": "LOWSTOCK-001",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": 99.99,
            "quantity_in_stock": 1,
            "min_stock_level": 5,
            "unit_of_measure": "шт",
        }
        client.post("/products/", json=product_data, headers=auth_headers)

        response = client.get("/products/low-stock/list", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        products = response.json()
        assert len(products) >= 1
