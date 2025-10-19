import pytest
from src.masks import get_mask_account, get_mask_card_number, mask_financial_data


class TestMasks:
    """Тесты для модуля masks с параметризацией"""

    # Параметризованные тесты для get_mask_card_number
    @pytest.mark.parametrize("card_number,expected", [
        # Стандартные номера карт (16 цифр) - маскируются
        ("1234567812345678", "1234 56** **** 5678"),
        ("1234567890123456", "1234 56** **** 3456"),
        ("5555666677778888", "5555 66** **** 8888"),
        # Номера с пробелами и разделителями - извлекаются цифры и маскируются
        ("1234 5678 1234 5678", "1234 56** **** 5678"),
        ("1234-5678-1234-5678", "1234 56** **** 5678"),
        ("1234.5678.1234.5678", "1234 56** **** 5678"),
        # Номера с текстом - извлекаются цифры и маскируются
        ("Card 1234567812345678", "1234 56** **** 5678"),
        ("Visa 1234-5678-1234-5678", "1234 56** **** 5678"),
    ])
    def test_get_mask_card_number_valid(self, card_number, expected):
        """Тест маскировки валидных номеров карт"""
        result = get_mask_card_number(card_number)
        assert result == expected

    @pytest.mark.parametrize("card_number,expected", [
        # Не 16 цифр - возвращаются как есть
        ("12345678", "12345678"),  # короткий номер
        ("123456781234567890", "123456781234567890"),  # длинный номер
        ("", ""),  # пустая строка
        ("1234", "1234"),  # слишком короткий
        # С буквами - возвращается исходная строка если не 16 цифр
        ("abcd1234efgh5678", "abcd1234efgh5678"),  # только 8 цифр
        ("1234abcd5678efgh", "1234abcd5678efgh"),  # только 8 цифр
    ])
    def test_get_mask_card_number_invalid_length(self, card_number, expected):
        """Тест маскировки номеров карт с неправильной длиной"""
        result = get_mask_card_number(card_number)
        assert result == expected

    @pytest.mark.parametrize("invalid_input,expected", [
        (None, ""),  # None возвращает пустую строку
        (1234567812345678, "1234567812345678"),  # число возвращается как строка
        (12345678, "12345678"),  # короткое число возвращается как строка
        (["1234567812345678"], "['1234567812345678']"),  # список возвращается как строка
        ([1234567812345678], "[1234567812345678]"),  # список с числом возвращается как строка
    ])
    def test_get_mask_card_number_invalid_input(self, invalid_input, expected):
        """Тест обработки невалидных входных данных для карт"""
        result = get_mask_card_number(invalid_input)
        assert result == expected

    # Параметризованные тесты для get_mask_account
    @pytest.mark.parametrize("account_number,expected", [
        # Стандартные номера счетов - извлекаются цифры и маскируются
        ("12345678901234567890", "**7890"),
        ("11112222333344445555", "**5555"),
        ("99998888777766665544", "**5544"),
        # Короткие номера счетов
        ("1234567890", "**7890"),  # 10 цифр
        ("1234", "**1234"),  # 4 цифры - минимальная длина для маскировки
        # С пробелами, разделителями и буквами - извлекаются цифры и маскируются
        ("1234 5678 9012 3456 7890", "**7890"),
        ("1234-5678-9012-3456-7890", "**7890"),
        ("abcd12345678901234567890", "**7890"),
        ("Счет 12345678901234567890", "**7890"),
        ("Account 12345678901234567890", "**7890"),
    ])
    def test_get_mask_account_valid(self, account_number, expected):
        """Тест маскировки валидных номеров счетов"""
        result = get_mask_account(account_number)
        assert result == expected

    @pytest.mark.parametrize("account_number,expected", [
        ("12", "12"),  # слишком короткий для маскировки
        ("", ""),  # пустая строка
        ("abc", "abc"),  # нет цифр
        ("Счет 123", "Счет 123"),  # недостаточно цифр
    ])
    def test_get_mask_account_invalid_length(self, account_number, expected):
        """Тест маскировки номеров счетов с недостаточным количеством цифр"""
        result = get_mask_account(account_number)
        assert result == expected

    @pytest.mark.parametrize("invalid_input,expected", [
        (None, ""),  # None возвращает пустую строку
        (12345678901234567890, "12345678901234567890"),  # число возвращается как строка
        (1234, "1234"),  # число возвращается как строка
        (12, "12"),  # число возвращается как строка
        ([], "[]"),  # пустой список возвращается как строка
    ])
    def test_get_mask_account_invalid_input(self, invalid_input, expected):
        """Тест обработки невалидных входных данных для счетов"""
        result = get_mask_account(invalid_input)
        assert result == expected

    # Тесты для универсальной функции mask_financial_data
    @pytest.mark.parametrize("data,expected", [
        ("1234567812345678", "1234 56** **** 5678"),  # карта
        ("1234 5678 1234 5678", "1234 56** **** 5678"),  # карта с пробелами
        ("12345678901234567890", "**7890"),  # счет
        ("Счет 12345678901234567890", "**7890"),  # счет с текстом
        ("1234", "**1234"),  # короткий счет
        ("12", "12"),  # слишком короткий
        (None, ""),  # None
        (1234567812345678, "1234567812345678"),  # число
    ])
    def test_mask_financial_data(self, data, expected):
        """Тест универсальной функции маскирования"""
        result = mask_financial_data(data)
        assert result == expected


def test_integration():
    """Интеграционный тест всех функций маскирования"""
    # Тест карт
    assert get_mask_card_number("1234567812345678") == "1234 56** **** 5678"
    assert get_mask_card_number("1234-5678-1234-5678") == "1234 56** **** 5678"

    # Тест счетов
    assert get_mask_account("12345678901234567890") == "**7890"
    assert get_mask_account("Счет 12345678901234567890") == "**7890"

    # Тест универсальной функции
    assert mask_financial_data("1234567812345678") == "1234 56** **** 5678"
    assert mask_financial_data("12345678901234567890") == "**7890"
