import pytest
from src.masks import get_mask_card_number, get_mask_account


class TestMasks:
    """Тесты для модуля masks"""

    # Тесты для get_mask_card_number
    def test_get_mask_card_number_standard(self):
        """Тест стандартного номера карты"""
        result = get_mask_card_number("1234567812345678")
        assert result == "1234 56** **** 5678"

    def test_get_mask_card_number_different_length(self):
        """Тест номера карты разной длины"""
        result = get_mask_card_number("1234567890123456")
        assert result == "1234 56** **** 3456"

    def test_get_mask_card_number_short(self):
        """Тест короткого номера карты"""
        result = get_mask_card_number("12345678")
        assert result == "1234 56** **** 5678"  # или ожидаемое поведение для коротких номеров

    def test_get_mask_card_number_empty(self):
        """Тест пустой строки"""
        with pytest.raises(ValueError):
            get_mask_card_number("")

    def test_get_mask_card_number_none(self):
        """Тест None значения"""
        with pytest.raises(TypeError):
            get_mask_card_number(None)

    def test_get_mask_card_number_with_spaces(self):
        """Тест номера карты с пробелами"""
        result = get_mask_card_number("1234 5678 1234 5678")
        assert result == "1234 56** **** 5678"

    # Тесты для get_mask_account
    def test_get_mask_account_standard(self):
        """Тест стандартного номера счета"""
        result = get_mask_account("12345678901234567890")
        assert result == "**7890"

    def test_get_mask_account_short(self):
        """Тест короткого номера счета"""
        result = get_mask_account("123456")
        assert result == "**3456"  # или ожидаемое поведение для коротких номеров

    def test_get_mask_account_empty(self):
        """Тест пустой строки"""
        with pytest.raises(ValueError):
            get_mask_account("")

    def test_get_mask_account_none(self):
        """Тест None значения"""
        with pytest.raises(TypeError):
            get_mask_account(None)

    def test_get_mask_account_exact_length(self):
        """Тест номера счета минимальной длины"""
        result = get_mask_account("1234567890")
        assert result == "**7890"

    @pytest.mark.parametrize("account_number,expected", [
        ("12345678901234567890", "**7890"),
        ("11112222333344445555", "**5555"),
        ("99998888777766665544", "**5544"),
        ("1234", "**1234"),  # граничный случай
    ])
    def test_get_mask_account_parametrized(self, account_number, expected):
        """Параметризованный тест для get_mask_account"""
        result = get_mask_account(account_number)
        assert result == expected