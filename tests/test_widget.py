import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from widget import mask_account_card, get_date


def test_mask_account_card_account():
    """Тест маскировки счета"""
    result = mask_account_card("Счет 12345678901234567890")
    assert "Счет" in result
    assert "**7890" in result


def test_mask_account_card_credit_card():
    """Тест маскировки кредитной карты"""
    result = mask_account_card("Visa Platinum 1234567812345678")
    assert "Visa Platinum" in result
    assert "1234 56** **** 5678" in result


def test_mask_account_card_empty():
    """Тест маскировки пустой строки"""
    assert mask_account_card("") == ""
    assert mask_account_card(None) == ""


def test_mask_account_card_invalid():
    """Тест маскировки некорректной строки"""
    result = mask_account_card("Invalid string")
    assert result == "Invalid string"


def test_mask_account_card_short_card():
    """Тест маскировки короткого номера карты"""
    result = mask_account_card("Visa 1234")
    assert result == "Visa 1234"  # должен вернуть исходную строку


def test_mask_account_card_short_account():
    """Тест маскировки короткого счета"""
    result = mask_account_card("Счет 123")
    assert result == "Счет 123"  # должен вернуть исходную строку


def test_get_date_iso_format():
    """Тест преобразования даты из ISO формата"""
    result = get_date("2023-01-15T10:30:00")
    assert result == "15.01.2023"


def test_get_date_date_only():
    """Тест преобразования даты без времени"""
    result = get_date("2023-01-15")
    assert result == "15.01.2023"


def test_get_date_invalid():
    """Тест преобразования некорректной даты"""
    result = get_date("invalid-date")
    assert result == "invalid-date"


def test_get_date_none():
    """Тест преобразования None"""
    assert get_date(None) == ""


def test_get_date_custom_format():
    """Тест преобразования даты в нестандартном формате"""
    result = get_date("15/01/2023")
    assert result == "15/01/2023"  # должен вернуть исходную строку
