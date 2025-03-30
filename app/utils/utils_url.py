import hashlib
import base64
from datetime import datetime, timedelta, timezone
from config import DEFAULT_LINK_EXPIRY_DAYS

"""Генерируем короткий код для URL"""
def generate_short_code(url: str, length: int = 8) -> str:
    hash_object = hashlib.sha256(url.encode())
    hash_hex = hash_object.hexdigest()
    
    short_code = base64.urlsafe_b64encode(hash_hex[:10].encode()).decode()[:length]
    return short_code.replace('_', '-').replace('=', '')

"""Проверяет, истек ли срок действия ссылки"""
def is_link_expired(expires_at: datetime) -> bool:
    if not expires_at:
        return False
    return datetime.now(timezone.utc) > expires_at

"""Возвращает дату истечения по умолчанию"""
def get_default_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=DEFAULT_LINK_EXPIRY_DAYS)
