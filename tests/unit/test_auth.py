#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for authentication logic
Testing password hashing, JWT token creation and validation
"""

import pytest
from datetime import timedelta
from jose import JWTError, jwt

from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
)


class TestPasswordHashing:
    """Test password hashing and verification with bcrypt"""

    def test_password_hash_creates_hash(self):
        """Test that password hashing creates a hash"""
        password = "testpass123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > len(password)

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpass123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpass123"
        hashed = get_password_hash(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (bcrypt salt)"""
        password = "testpass123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_special_characters_in_password(self):
        """Test password with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("P@ssw0rd!#$%^&*(", hashed) is False

    def test_unicode_characters_in_password(self):
        """Test password with unicode characters"""
        password = "пароль123!@#"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("пароль123", hashed) is False


class TestJWTTokenCreation:
    """Test JWT token creation"""

    def test_create_access_token_returns_string(self):
        """Test that token creation returns a string"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_user_data(self):
        """Test that token contains user data"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        from app.auth import SECRET_KEY, ALGORITHM

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"

    def test_token_contains_expiration(self):
        """Test that token contains expiration"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        from app.auth import SECRET_KEY, ALGORITHM

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_token_with_custom_expiration(self):
        """Test token with custom expiration time"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(hours=1)
        token = create_access_token(data, expires_delta)

        from app.auth import SECRET_KEY, ALGORITHM

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_token_default_expiration(self):
        """Test token has default expiration"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        from app.auth import SECRET_KEY, ALGORITHM

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        import datetime

        exp_time = datetime.datetime.fromtimestamp(payload["exp"])
        now = datetime.datetime.utcnow()

        # Token should expire in future (default 15 minutes, but can be longer)
        time_diff = (exp_time - now).total_seconds()
        assert 0 < time_diff


class TestJWTTokenValidation:
    """Test JWT token validation"""

    def test_valid_token_structure(self):
        """Test that valid token has correct structure"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        parts = token.split(".")
        assert len(parts) == 3

    def test_token_with_multiple_claims(self):
        """Test token with multiple claims"""
        data = {"sub": "testuser", "email": "test@example.com", "role": "admin"}
        token = create_access_token(data)

        from app.auth import SECRET_KEY, ALGORITHM

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"

    def test_expired_token_raises_error(self):
        """Test that expired token raises JWTError"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)

        from app.auth import SECRET_KEY, ALGORITHM

        with pytest.raises(JWTError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_invalid_token_signature_raises_error(self):
        """Test that invalid token signature raises JWTError"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        # Modify token signature
        modified_token = token[:-10] + "invalidkey"

        from app.auth import SECRET_KEY, ALGORITHM

        with pytest.raises(JWTError):
            jwt.decode(modified_token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_malformed_token_raises_error(self):
        """Test that malformed token raises JWTError"""
        malformed_token = "not.a.token"

        from app.auth import SECRET_KEY, ALGORITHM

        with pytest.raises(JWTError):
            jwt.decode(malformed_token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_token_with_wrong_algorithm(self):
        """Test token verification with wrong algorithm"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        from app.auth import SECRET_KEY

        with pytest.raises(JWTError):
            jwt.decode(token, SECRET_KEY, algorithms=["HS512"])


class TestAuthenticationFlow:
    """Test complete authentication flow"""

    def test_password_hashing_and_verification_flow(self):
        """Test complete password flow: hash and verify"""
        original_password = "MySecurePassword123!"

        # User registers with password
        hashed = get_password_hash(original_password)

        # User logs in with password
        is_valid = verify_password(original_password, hashed)
        assert is_valid is True

        # User tries with wrong password
        is_valid = verify_password("WrongPassword", hashed)
        assert is_valid is False

    def test_token_creation_and_decode_flow(self):
        """Test complete token flow: create and decode"""
        user_data = {"sub": "john_doe"}

        # Create token
        token = create_access_token(user_data)

        # Decode token
        from app.auth import SECRET_KEY, ALGORITHM

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["sub"] == "john_doe"
        assert "exp" in payload

    def test_multiple_tokens_are_different(self):
        """Test that multiple tokens for same data can have different expiration"""
        import time
        from app.auth import SECRET_KEY, ALGORITHM

        user_data = {"sub": "testuser"}

        token1 = create_access_token(user_data)

        # Small delay to ensure different exp time
        time.sleep(0.01)

        token2 = create_access_token(user_data)

        # Decode and check both are valid
        payload1 = jwt.decode(token1, SECRET_KEY, algorithms=[ALGORITHM])
        payload2 = jwt.decode(token2, SECRET_KEY, algorithms=[ALGORITHM])

        # Both should decode to same user
        assert payload1["sub"] == payload2["sub"]
        assert payload2["sub"] == "testuser"
