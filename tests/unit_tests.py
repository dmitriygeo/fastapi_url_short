import pytest
from datetime import datetime, timezone, timedelta
from app.utils.utils_url import generate_short_code, is_link_expired, get_default_expiry


def test_generate_short_code():
    # Проверка генерации короткого кода
    url = "https://example.com"
    code = generate_short_code(url)
    assert len(code) == 8  # Проверяем длину кода по умолчанию
    assert "-" not in code  # Проверяем, что символы "_" и "=" заменены
    assert "=" not in code


def test_generate_short_code_custom_length():
    # Проверка генерации короткого кода с пользовательской длиной
    url = "https://example.com"
    code = generate_short_code(url, length=4)
    assert len(code) == 4


def test_is_link_expired():
    # Проверка функции истечения срока ссылки
    future = datetime.now(timezone.utc) + timedelta(days=1)
    past = datetime.now(timezone.utc) - timedelta(days=1)

    assert not is_link_expired(future)  # Будущая дата не истекла
    assert is_link_expired(past)  # Прошедшая дата истекла
    assert not is_link_expired(None)  # Отсутствие даты = не истекла


def test_get_default_expiry():
    # Проверка функции получения даты истечения по умолчанию
    default_expiry = get_default_expiry()
    now = datetime.now(timezone.utc)

    # Проверяем, что дата истечения в будущем
    assert default_expiry > now

    # Проверяем, что дата истечения примерно соответствует DEFAULT_LINK_EXPIRY_DAYS
    from config import DEFAULT_LINK_EXPIRY_DAYS
    days = int(DEFAULT_LINK_EXPIRY_DAYS)  # Преобразуем строку в число
    expected = now + timedelta(days=days)
    difference = abs((default_expiry - expected).total_seconds())
    assert difference < 10  # Разница меньше 10 секунд


