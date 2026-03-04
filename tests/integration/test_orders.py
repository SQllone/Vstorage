#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for orders endpoints
Testing CRUD operations for orders
"""

from fastapi import status


class TestOrderCRUD:
    """Test order CRUD operations"""

    def test_create_order(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test creating an order"""
        # Create category and product
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        product_data = {
            "name": "Test Product",
            "description": "Test",
            "sku": "TEST-SKU-001",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": 99.99,
            "quantity_in_stock": 10,
            "min_stock_level": 2,
            "unit_of_measure": "шт",
        }
        prod_response = client.post(
            "/products/", json=product_data, headers=auth_headers
        )
        product_id = prod_response.json()["id"]

        # Create order
        order_data = {
            "order_type": "supply",
            "supplier_id": supplier_id,
            "notes": "Test order",
            "items": [{"product_id": product_id, "quantity": 5, "unit_price": 99.99}],
        }
        response = client.post("/orders/", json=order_data, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["order_type"] == "supply"
        assert len(data["items"]) == 1
        assert "id" in data

    def test_get_orders(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test getting list of orders"""
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        product_data = {
            "name": "Test Product 2",
            "description": "Test",
            "sku": "TEST-SKU-002",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": 49.99,
            "quantity_in_stock": 20,
            "min_stock_level": 1,
            "unit_of_measure": "шт",
        }
        prod_response = client.post(
            "/products/", json=product_data, headers=auth_headers
        )
        product_id = prod_response.json()["id"]

        order_data = {
            "order_type": "shipment",
            "supplier_id": supplier_id,
            "notes": "Test shipment",
            "items": [{"product_id": product_id, "quantity": 3, "unit_price": 49.99}],
        }
        client.post("/orders/", json=order_data, headers=auth_headers)

        response = client.get("/orders/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        orders = response.json()
        assert len(orders) >= 1

    def test_get_order_by_id(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test getting single order by ID"""
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        product_data = {
            "name": "Test Product 3",
            "description": "Test",
            "sku": "TEST-SKU-003",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": 199.99,
            "quantity_in_stock": 15,
            "min_stock_level": 2,
            "unit_of_measure": "шт",
        }
        prod_response = client.post(
            "/products/", json=product_data, headers=auth_headers
        )
        product_id = prod_response.json()["id"]

        order_data = {
            "order_type": "supply",
            "supplier_id": supplier_id,
            "notes": "Test order",
            "items": [{"product_id": product_id, "quantity": 2, "unit_price": 199.99}],
        }
        create_response = client.post("/orders/", json=order_data, headers=auth_headers)
        order_id = create_response.json()["id"]

        response = client.get(f"/orders/{order_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == order_id
        assert data["order_type"] == "supply"

    def test_update_order_status(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test updating order status"""
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        product_data = {
            "name": "Test Product 4",
            "description": "Test",
            "sku": "TEST-SKU-004",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": 299.99,
            "quantity_in_stock": 8,
            "min_stock_level": 1,
            "unit_of_measure": "шт",
        }
        prod_response = client.post(
            "/products/", json=product_data, headers=auth_headers
        )
        product_id = prod_response.json()["id"]

        order_data = {
            "order_type": "supply",
            "supplier_id": supplier_id,
            "notes": "Test order",
            "items": [{"product_id": product_id, "quantity": 1, "unit_price": 299.99}],
        }
        create_response = client.post("/orders/", json=order_data, headers=auth_headers)
        order_id = create_response.json()["id"]

        update_data = {"status": "completed"}
        response = client.put(
            f"/orders/{order_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"

    def test_delete_order(
        self, client, auth_headers, test_category_data, test_supplier_data
    ):
        """Test deleting an order"""
        cat_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = cat_response.json()["id"]

        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        product_data = {
            "name": "Test Product 5",
            "description": "Test",
            "sku": "TEST-SKU-005",
            "category_id": category_id,
            "supplier_id": supplier_id,
            "price": 149.99,
            "quantity_in_stock": 12,
            "min_stock_level": 1,
            "unit_of_measure": "шт",
        }
        prod_response = client.post(
            "/products/", json=product_data, headers=auth_headers
        )
        product_id = prod_response.json()["id"]

        order_data = {
            "order_type": "shipment",
            "supplier_id": supplier_id,
            "notes": "Test order",
            "items": [{"product_id": product_id, "quantity": 4, "unit_price": 149.99}],
        }
        create_response = client.post("/orders/", json=order_data, headers=auth_headers)
        order_id = create_response.json()["id"]

        response = client.delete(f"/orders/{order_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_create_order_empty_items(self, client, auth_headers, test_supplier_data):
        """Test creating order with empty items"""
        sup_response = client.post(
            "/suppliers/", json=test_supplier_data, headers=auth_headers
        )
        supplier_id = sup_response.json()["id"]

        order_data = {
            "order_type": "supply",
            "supplier_id": supplier_id,
            "notes": "Test order",
            "items": [],
        }
        response = client.post("/orders/", json=order_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_order_statistics(self, client, auth_headers):
        """Test getting order statistics"""
        response = client.get("/orders/stats/overview", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_products" in data
        assert "total_orders" in data
