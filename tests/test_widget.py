import pytest

from src.widget import get_date, mask_account_card


class TestWidget:
    """Тесты для модуля widget"""

    # Тесты для mask_account_card
    @pytest.mark.parametrize("input_string,expected", [
        ("Visa Platinum 1234567812345678", "Visa Platinum 1234 56** **** 5678"),
        ("Счет 12345678901234567890", "Счет **7890"),
        ("", ""),
    ])
    def test_mask_account_card(self, input_string, expected):
        result = mask_account_card(input_string)
        assert result == expected

    # Тесты для get_date
    @pytest.mark.parametrize("date_string,expected", [
        ("2023-10-01T12:00:00.000000", "01.10.2023"),
        ("2023-10-01", "01.10.2023"),
    ])
    def test_get_date(self, date_string, expected):
        result = get_date(date_string)
        assert result == expected