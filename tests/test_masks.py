import pytest
from src.masks import get_mask_card_number, get_mask_account


class TestMasks:
    """Тесты для функций маскирования"""

    def test_get_mask_card_number_valid(self):
        """Тест маскирования валидных номеров карт"""
        # Стандартные номера карт (16 цифр) - маскируются
        assert get_mask_card_number("1234567812345678") == "1234 56** **** 5678"
        assert get_mask_card_number("1234567890123456") == "1234 56** **** 3456"
        assert get_mask_card_number("5555666677778888") == "5555 66** **** 8888"

    def test_get_mask_card_number_with_spaces(self):
        """Тест маскирования номеров карт с пробелами"""
        assert get_mask_card_number("1234 5678 1234 5678") == "1234 56** **** 5678"
        assert get_mask_card_number("1234-5678-1234-5678") == "1234 56** **** 5678"

    def test_get_mask_card_number_invalid_length(self):
        """Тест маскирования номеров карт с неправильной длиной"""
        # Короткие номера - возвращаются как есть
        assert get_mask_card_number("12345678") == "12345678"
        assert get_mask_card_number("1234") == "1234"

        # Длинные номера - возвращаются как есть
        assert get_mask_card_number("123456781234567890") == "123456781234567890"

    def test_get_mask_card_number_empty(self):
        """Тест маскирования пустых номеров карт"""
        assert get_mask_card_number("") == ""
        assert get_mask_card_number(None) == ""

    def test_get_mask_card_number_non_string(self):
        """Тест маскирования не-строковых номеров карт"""
        assert get_mask_card_number(1234567812345678) == "1234567812345678"
        assert get_mask_card_number(1234) == "1234"
