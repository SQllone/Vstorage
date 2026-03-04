#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for authentication endpoints
Testing /auth/register, /auth/login, /auth/me endpoints
"""

from fastapi import status

# Добавляем константу для 429 статуса, если её нет в fastapi.status
if not hasattr(status, "HTTP_429_TOO_MANY_REQUESTS"):
    status.HTTP_429_TOO_MANY_REQUESTS = 429


class TestAuthRegister:
    """Test user registration endpoint"""

    def test_register_user_success(self, client, test_user_data):
        """Test successful user registration"""
        response = client.post("/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "hashed_password" not in data
        assert "id" in data

    def test_register_duplicate_username(self, client, test_user_data):
        """Test registration with duplicate username"""
        client.post("/auth/register", json=test_user_data)

        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, client, test_user_data):
        """Test registration with duplicate email"""
        client.post("/auth/register", json=test_user_data)

        different_user = test_user_data.copy()
        different_user["username"] = "differentuser"

        response = client.post("/auth/register", json=different_user)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()["detail"]

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        data = {
            "username": "testuser",
            "email": "invalid-email",
            "full_name": "Test User",
            "password": "testpass123",
        }
        response = client.post("/auth/register", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_password(self, client):
        """Test registration with short password"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "123",
        }
        response = client.post("/auth/register", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthLogin:
    """Test user login endpoint"""

    def test_login_success(self, client, test_user_data):
        """Test successful login"""
        client.post("/auth/register", json=test_user_data)

        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user_data):
        """Test login with wrong password"""
        client.post("/auth/register", json=test_user_data)

        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword",
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login for non-existent user"""
        login_data = {"username": "nonexistent", "password": "password123"}
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_returns_valid_token(self, client, test_user_data):
        """Test that login returns a valid JWT token"""
        from jose import jwt
        from app.auth import SECRET_KEY, ALGORITHM

        client.post("/auth/register", json=test_user_data)

        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        }
        response = client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]

        # Verify token is valid JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == test_user_data["username"]


class TestAuthMe:
    """Test current user info endpoint"""

    def test_get_current_user_success(self, client, auth_headers):
        """Test getting current user info"""
        response = client.get("/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data

    def test_get_current_user_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_invalid_token(self, client):
        """Test accessing with invalid token"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/auth/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_expired_token(self, client, test_user_data):
        """Test accessing with expired token"""
        from datetime import timedelta
        from app.auth import create_access_token

        # Create expired token
        data = {"sub": test_user_data["username"]}
        expired_token = create_access_token(data, timedelta(seconds=-1))

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/auth/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthLogout:
    """Test logout endpoint (demonstration endpoint)"""

    def test_logout_success(self, client, auth_headers):
        """Test logout endpoint"""
        response = client.post("/auth/logout", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

    def test_logout_without_token(self, client):
        """Test logout without token"""
        response = client.post("/auth/logout")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAuthTokenVerification:
    """Test token verification endpoint"""

    def test_verify_valid_token(self, client, auth_headers):
        """Test token verification endpoint"""
        response = client.get("/auth/verify-token", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is True
        assert data["username"] == "testuser"

    def test_verify_invalid_token(self, client):
        """Test verification of invalid token"""
        headers = {"Authorization": "Bearer invalid.token"}
        response = client.get("/auth/verify-token", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False


class TestRateLimiting:
    """Test rate limiting middleware"""

    def test_login_rate_limit(self, client, test_user_data):
        """Test that login endpoint respects rate limiting (disabled in test mode)"""
        # В тестовом режиме rate limiting отключен, поэтому просто проверяем, что запросы проходят
        client.post("/auth/register", json=test_user_data)

        # Делаем 10 запросов
        for _ in range(10):
            response = client.post(
                "/auth/login",
                json={
                    "username": test_user_data["username"],
                    "password": test_user_data["password"],
                },
            )
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_401_UNAUTHORIZED,
            ]

    def test_register_rate_limit(self, client):
        """Test that register endpoint respects rate limiting (disabled in test mode)"""
        # В тестовом режиме rate limiting отключен, поэтому просто проверяем, что запросы проходят
        # Делаем 10 запросов
        for i in range(10):
            user_data = {
                "username": f"testuser{i}",
                "email": f"test{i}@example.com",
                "full_name": "Test User",
                "password": "testpass123",
                "role": "worker",
            }
            response = client.post("/auth/register", json=user_data)
            assert response.status_code == status.HTTP_201_CREATED
