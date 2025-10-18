import pytest
from src.widget import mask_account_card, get_date


def test_mask_account_card_empty_string():
    """Тест маскировки пустой строки."""
    result = mask_account_card("")
    assert result == ""


def test_mask_account_card_none():
    """Тест маскировки None."""
    result = mask_account_card(None)
    assert result == ""


def test_mask_account_card_short_number():
    """Тест маскировки строки с коротким номером."""
    result = mask_account_card("1234")
    assert result == "1234"


def test_mask_account_card_no_digits():
    """Тест маскировки строки без цифр."""
    result = mask_account_card("Только текст")
    assert result == "Только текст"


def test_get_date_invalid_format():
    """Тест получения даты из невалидной строки."""
    result = get_date("invalid-date-format")
    assert result == "invalid-date-format"  # Должен вернуть исходную строку


def test_get_date_none():
    """Тест получения даты из None."""
    result = get_date(None)
    assert result == ""  # Теперь возвращает пустую строку


def test_get_date_without_t():
    """Тест получения даты из строки без 'T'."""
    result = get_date("2023-12-31")
    assert result == "31.12.2023"


def test_get_date_with_t():
    """Тест получения даты из строки с 'T'."""
    result = get_date("2023-12-31T10:30:00.000000")
    assert result == "31.12.2023"


def test_get_date_invalid_parts():
    """Тест получения даты с неправильным количеством частей."""
    result = get_date("2023-12")
    assert result == "2023-12"


def test_get_date_empty_string():
    """Тест получения даты из пустой строки."""
    result = get_date("")
    assert result == ""
