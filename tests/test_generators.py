"""
Тесты для модуля generators.
"""

import pytest

from src.generators import filter_by_currency, transaction_descriptions, card_number_generator


@pytest.fixture
def sample_transactions():
    """Фикстура с примером транзакций для тестирования."""
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {
                "amount": "9824.07",
                "currency": {"name": "USD", "code": "USD"}
            },
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702"
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {
                "amount": "79114.93",
                "currency": {"name": "USD", "code": "USD"}
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188"
        },
        {
            "id": 873106923,
            "state": "EXECUTED",
            "date": "2019-03-23T01:09:46.296404",
            "operationAmount": {
                "amount": "43318.34",
                "currency": {"name": "руб.", "code": "RUB"}
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 44812258784861134719",
            "to": "Счет 74489636417521191160"
        },
        {
            "id": 895315941,
            "state": "EXECUTED",
            "date": "2018-08-19T04:27:37.904916",
            "operationAmount": {
                "amount": "56883.54",
                "currency": {"name": "USD", "code": "USD"}
            },
            "description": "Перевод с карты на карту",
            "from": "Visa Classic 6831982476737658",
            "to": "Visa Platinum 8990922113665229"
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
            "operationAmount": {
                "amount": "67314.70",
                "currency": {"name": "руб.", "code": "RUB"}
            },
            "description": "Перевод организации",
            "from": "Visa Platinum 1246377376343588",
            "to": "Счет 14211924144426031657"
        }
    ]


class TestFilterByCurrency:
    """Тесты для функции filter_by_currency."""

    def test_filter_usd_transactions(self, sample_transactions):
        """Тест фильтрации USD транзакций."""
        usd_transactions = filter_by_currency(sample_transactions, "USD")

        usd_list = list(usd_transactions)
        assert len(usd_list) == 3
        assert all(txn['operationAmount']['currency']['code'] == 'USD' for txn in usd_list)
        assert usd_list[0]['id'] == 939719570
        assert usd_list[1]['id'] == 142264268
        assert usd_list[2]['id'] == 895315941

    def test_filter_rub_transactions(self, sample_transactions):
        """Тест фильтрации RUB транзакций."""
        rub_transactions = filter_by_currency(sample_transactions, "RUB")

        rub_list = list(rub_transactions)
        assert len(rub_list) == 2
        assert all(txn['operationAmount']['currency']['code'] == 'RUB' for txn in rub_list)
        assert rub_list[0]['id'] == 873106923
        assert rub_list[1]['id'] == 594226727

    def test_filter_eur_transactions_empty(self, sample_transactions):
        """Тест фильтрации несуществующей валюты."""
        eur_transactions = filter_by_currency(sample_transactions, "EUR")
        eur_list = list(eur_transactions)
        assert len(eur_list) == 0

    def test_filter_empty_transactions(self):
        """Тест фильтрации пустого списка транзакций."""
        empty_transactions = filter_by_currency([], "USD")
        assert list(empty_transactions) == []

    def test_filter_transactions_with_missing_currency(self):
        """Тест фильтрации транзакций с отсутствующей валютой."""
        transactions_with_missing = [
            {"id": 1, "operationAmount": {"amount": "100"}},  # Нет currency
            {"id": 2, "operationAmount": {"amount": "200", "currency": {}}},  # Пустой currency
            {"id": 3, "operationAmount": {"amount": "300", "currency": {"name": "USD"}}}  # Нет code
        ]

        usd_transactions = filter_by_currency(transactions_with_missing, "USD")
        assert list(usd_transactions) == []


class TestTransactionDescriptions:
    """Тесты для функции transaction_descriptions."""

    def test_descriptions_generator(self, sample_transactions):
        """Тест генератора описаний транзакций."""
        desc_gen = transaction_descriptions(sample_transactions)

        # Проверяем последовательное получение описаний
        assert next(desc_gen) == "Перевод организации"
        assert next(desc_gen) == "Перевод со счета на счет"
        assert next(desc_gen) == "Перевод со счета на счет"
        assert next(desc_gen) == "Перевод с карты на карту"
        assert next(desc_gen) == "Перевод организации"

        # Проверяем конец итератора
        with pytest.raises(StopIteration):
            next(desc_gen)

    def test_descriptions_empty_list(self):
        """Тест генератора с пустым списком транзакций."""
        desc_gen = transaction_descriptions([])

        with pytest.raises(StopIteration):
            next(desc_gen)

    def test_descriptions_single_transaction(self):
        """Тест генератора с одной транзакцией."""
        single_transaction = [{"description": "Одна транзакция"}]
        desc_gen = transaction_descriptions(single_transaction)

        assert next(desc_gen) == "Одна транзакция"

        with pytest.raises(StopIteration):
            next(desc_gen)


class TestCardNumberGenerator:
    """Тесты для функции card_number_generator."""

    def test_small_range(self):
        """Тест генератора с небольшим диапазоном."""
        card_gen = card_number_generator(1, 5)

        expected_numbers = [
            "0000 0000 0000 0001",
            "0000 0000 0000 0002",
            "0000 0000 0000 0003",
            "0000 0000 0000 0004",
            "0000 0000 0000 0005"
        ]

        for expected in expected_numbers:
            assert next(card_gen) == expected

        with pytest.raises(StopIteration):
            next(card_gen)

    def test_single_number(self):
        """Тест генератора с одним номером."""
        card_gen = card_number_generator(9999, 9999)

        assert next(card_gen) == "0000 0000 0000 9999"

        with pytest.raises(StopIteration):
            next(card_gen)

    def test_large_numbers(self):
        """Тест генератора с большими номерами."""
        card_gen = card_number_generator(9999999999999998, 9999999999999999)

        assert next(card_gen) == "9999 9999 9999 9998"
        assert next(card_gen) == "9999 9999 9999 9999"

        with pytest.raises(StopIteration):
            next(card_gen)

    def test_format_correctness(self):
        """Тест правильности форматирования номеров."""
        card_gen = card_number_generator(1234567890123456, 1234567890123456)

        card_number = next(card_gen)
        assert card_number == "1234 5678 9012 3456"
        assert len(card_number) == 19  # 16 цифр + 3 пробела
        assert card_number.count(' ') == 3

    def test_invalid_range(self):
        """Тест генератора с неверным диапазоном (start > end)."""
        card_gen = card_number_generator(10, 5)

        # Должен вернуть пустую последовательность
        with pytest.raises(StopIteration):
            next(card_gen)

    def test_zero_start(self):
        """Тест генератора с началом с 0."""
        card_gen = card_number_generator(0, 2)

        assert next(card_gen) == "0000 0000 0000 0000"
        assert next(card_gen) == "0000 0000 0000 0001"
        assert next(card_gen) == "0000 0000 0000 0002"

        with pytest.raises(StopIteration):
            next(card_gen)


def test_generators_are_iterators(sample_transactions):
    """Тест, что все функции возвращают итераторы."""
    # filter_by_currency
    usd_gen = filter_by_currency(sample_transactions, "USD")
    assert hasattr(usd_gen, '__iter__')
    assert hasattr(usd_gen, '__next__')

    # transaction_descriptions
    desc_gen = transaction_descriptions(sample_transactions)
    assert hasattr(desc_gen, '__iter__')
    assert hasattr(desc_gen, '__next__')

    # card_number_generator
    card_gen = card_number_generator(1, 5)
    assert hasattr(card_gen, '__iter__')
    assert hasattr(card_gen, '__next__')
