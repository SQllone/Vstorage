#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for categories endpoints
Testing CRUD operations for categories
"""

from fastapi import status


class TestCategoryCRUD:
    """Test category CRUD operations"""

    def test_create_category(self, client, auth_headers, test_category_data):
        """Test creating a category"""
        response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == test_category_data["name"]
        assert data["description"] == test_category_data["description"]
        assert "id" in data

    def test_get_categories(self, client, auth_headers, test_category_data):
        """Test getting list of categories"""
        client.post("/categories/", json=test_category_data, headers=auth_headers)

        response = client.get("/categories/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        categories = response.json()
        assert len(categories) >= 1
        assert any(c["name"] == test_category_data["name"] for c in categories)

    def test_get_category_by_id(self, client, auth_headers, test_category_data):
        """Test getting single category by ID"""
        create_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = create_response.json()["id"]

        response = client.get(f"/categories/{category_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == test_category_data["name"]

    def test_update_category(self, client, auth_headers, test_category_data):
        """Test updating a category"""
        create_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = create_response.json()["id"]

        update_data = {"description": "Updated description"}
        response = client.patch(
            f"/categories/{category_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"

    def test_delete_category(self, client, auth_headers, test_category_data):
        """Test deleting a category"""
        create_response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = create_response.json()["id"]

        response = client.delete(f"/categories/{category_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        # Verify deletion
        response = client.get(f"/categories/{category_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_duplicate_category(self, client, auth_headers, test_category_data):
        """Test creating duplicate category"""
        client.post("/categories/", json=test_category_data, headers=auth_headers)

        response = client.post(
            "/categories/", json=test_category_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_category_empty_name(self, client, auth_headers):
        """Test creating category with empty name"""
        data = {"name": "", "description": "Test"}
        response = client.post("/categories/", json=data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_nonexistent_category(self, client, auth_headers):
        """Test getting non-existent category"""
        response = client.get("/categories/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_nonexistent_category(self, client, auth_headers):
        """Test updating non-existent category"""
        data = {"description": "Updated"}
        response = client.patch("/categories/99999", json=data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_protected_endpoint_no_auth(self, client, test_category_data):
        """Test that category endpoints require authentication"""
        response = client.post("/categories/", json=test_category_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
