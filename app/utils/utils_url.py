import hashlib
import base64
from datetime import datetime, timedelta, timezone
from config import DEFAULT_LINK_EXPIRY_DAYS

def generate_short_code(url: str, length: int = 8) -> str:
    """Генерируем короткий код для URL"""
    hash_object = hashlib.sha256(url.encode())
    hash_hex = hash_object.hexdigest()
    # Используем base64 для получения более короткого кода
    short_code = base64.urlsafe_b64encode(hash_hex[:10].encode()).decode()[:length]
    return short_code.replace('_', '-').replace('=', '')

def is_link_expired(expires_at: datetime) -> bool:
    """Проверяет, истек ли срок действия ссылки"""
    if not expires_at:
        return False
    return datetime.now(timezone.utc) > expires_at

def get_default_expiry() -> datetime:
    """Возвращает дату истечения по умолчанию"""
    return datetime.now(timezone.utc) + timedelta(days=DEFAULT_LINK_EXPIRY_DAYS)
