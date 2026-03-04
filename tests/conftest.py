#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures for VStorage tests
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Устанавливаем режим тестирования для отключения rate limiting
os.environ["TESTING"] = "true"

from main import app
from app.database import Base, get_db


@pytest.fixture(scope="function")
def test_db_engine():
    engine = create_engine(
        "sqlite:///./vstorage_test.db", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def client(test_db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpass123",
        "role": "worker",
    }


@pytest.fixture(scope="function")
def auth_headers(client, test_user_data):
    client.post("/auth/register", json=test_user_data)
    login_response = client.post(
        "/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_category_data():
    return {"name": "Electronics", "description": "Electronic devices"}


@pytest.fixture(scope="function")
def test_supplier_data():
    return {
        "name": "Tech Supplier Inc",
        "contact_person": "John Doe",
        "phone": "+7-495-123-45-67",
        "email": "supplier@example.com",
        "address": "123 Tech Street, Moscow",
    }


@pytest.fixture(scope="function", autouse=True)
def reset_rate_limiter():
    """Сбрасывает rate limiter между тестами"""
    from app.rate_limiter import limiter

    # Очищаем все лимиты
    if hasattr(limiter, "storage") and hasattr(limiter.storage, "storage"):
        limiter.storage.storage.clear()
    yield
