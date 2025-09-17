import pytest
from src.widget import mask_account_card, get_date


class TestWidget:
    """Тесты для модуля widget"""

    # Тесты для mask_account_card
    def test_mask_account_card_card_number(self):
        """Тест маскировки номера карты"""
        result = mask_account_card("Visa Platinum 1234567812345678")
        assert "1234 56** **** 5678" in result

    def test_mask_account_card_account_number(self):
        """Тест маскировки номера счета"""
        result = mask_account_card("Счет 12345678901234567890")
        assert "**7890" in result

    def test_mask_account_card_unknown_type(self):
        """Тест неизвестного типа"""
        result = mask_account_card("Неизвестный тип 1234567890")
        # Проверяем, что функция возвращает исходную строку или ожидаемое поведение
        assert "1234567890" in result or "**7890" in result

    def test_mask_account_card_empty(self):
        """Тест пустой строки"""
        result = mask_account_card("")
        assert result == ""

    def test_mask_account_card_none(self):
        """Тест None значения"""
        with pytest.raises(TypeError):
            mask_account_card(None)

    @pytest.mark.parametrize("input_string,expected_contains", [
        ("Visa 1234567812345678", "1234 56** **** 5678"),
        ("MasterCard 5555666677778888", "5555 66** **** 8888"),
        ("Счет 12345678901234567890", "**7890"),
        ("Maestro 1234123412341234", "1234 12** **** 1234"),
        ("American Express 123456789012345", "1234 56** **** 2345"),
    ])
    def test_mask_account_card_parametrized(self, input_string, expected_contains):
        """Параметризованный тест для mask_account_card"""
        result = mask_account_card(input_string)
        assert expected_contains in result

    # Тесты для get_date
    def test_get_date_standard_format(self):
        """Тест стандартного формата даты"""
        result = get_date("2023-10-01T12:00:00.000000")
        assert result == "01.10.2023"

    def test_get_date_different_format(self):
        """Тест другого формата даты"""
        result = get_date("2023-12-25T00:00:00.000000")
        assert result == "25.12.2023"

    def test_get_date_empty_string(self):
        """Тест пустой строки"""
        with pytest.raises(ValueError):
            get_date("")

    def test_get_date_invalid_format(self):
        """Тест неверного формата даты"""
        with pytest.raises(ValueError):
            get_date("invalid-date-format")

    def test_get_date_none(self):
        """Тест None значения"""
        with pytest.raises(TypeError):
            get_date(None)

    def test_get_date_without_time(self):
        """Тест даты без времени"""
        result = get_date("2023-10-01")
        assert result == "01.10.2023"

    @pytest.mark.parametrize("input_date,expected", [
        ("2023-01-15T08:30:00.000000", "15.01.2023"),
        ("2023-12-31T23:59:59.999999", "31.12.2023"),
        ("2020-02-29T12:00:00.000000", "29.02.2020"),  # високосный год
        ("1999-12-01T00:00:00.000000", "01.12.1999"),
    ])
    def test_get_date_parametrized(self, input_date, expected):
        """Параметризованный тест для get_date"""
        result = get_date(input_date)
        assert result == expected