"""
Модуль для настройки Rate Limiter
"""

from slowapi import Limiter
from fastapi import Request


def get_rate_limit_key(request: Request):
    """Получение ключа для rate limiting"""
    # В тестах TestClient может не иметь client.host, используем фиксированный ключ
    if request.client is None:
        return "test_client"
    return request.client.host


# Глобальный limiter
limiter = Limiter(key_func=get_rate_limit_key)
