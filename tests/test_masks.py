import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from masks import mask_card_number, mask_account_number


class TestMasks:
    """Тесты для masks.py"""

    def test_mask_card_number_normal(self):
        """Тест маскировки номера карты - нормальный случай"""
        result = mask_card_number("1234567812345678")
        assert result == "1234 56** **** 5678"

    def test_mask_card_number_with_spaces(self):
        """Тест маскировки номера карты с пробелами"""
        result = mask_card_number("1234 5678 1234 5678")
        assert result == "1234 56** **** 5678"

    def test_mask_card_number_short(self):
        """Тест маскировки короткого номера карты"""
        result = mask_card_number("1234")
        assert result == "1234"

    def test_mask_card_number_empty(self):
        """Тест маскировки пустого номера карты"""
        result = mask_card_number("")
        assert result == ""

    def test_mask_card_number_none(self):
        """Тест маскировки None"""
        result = mask_card_number(None)
        assert result == ""

    def test_mask_account_number_normal(self):
        """Тест маскировки номера счета - нормальный случай"""
        result = mask_account_number("1234567890123456")
        assert result == "Счет **3456"

    def test_mask_account_number_short(self):
        """Тест маскировки короткого номера счета"""
        result = mask_account_number("123")
        assert result == "123"

    def test_mask_account_number_empty(self):
        """Тест маскировки пустого номера счета"""
        result = mask_account_number("")
        assert result == ""

    def test_mask_account_number_none(self):
        """Тест маскировки None"""
        result = mask_account_number(None)
        assert result == ""
