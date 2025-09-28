from datetime import datetime

import pytest


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми данными для обработки транзакций"""
    return [
        {
            "id": 1,
            "state": "EXECUTED",
            "date": "2023-10-01T12:00:00.000000",
            "operationAmount": {"amount": "100.00", "currency": {"name": "USD"}},
            "description": "Перевод",
            "from": "Счет 12345678901234567890",
            "to": "Счет 09876543210987654321"
        },
        {
            "id": 2,
            "state": "PENDING",
            "date": "2023-09-15T08:30:00.000000",
            "operationAmount": {"amount": "50.00", "currency": {"name": "RUB"}},
            "description": "Покупка",
            "from": "Visa Platinum 1234567812345678",
            "to": "Счет 1111222233334444"
        },
        {
            "id": 3,
            "state": "EXECUTED",
            "date": "2023-11-20T16:45:00.000000",
            "operationAmount": {"amount": "200.00", "currency": {"name": "EUR"}},
            "description": "Оплата услуг",
            "from": "MasterCard 5555666677778888",
            "to": "Счет 9999888877776666"
        },
        {
            "id": 4,
            "state": "CANCELED",
            "date": "2023-08-05T10:15:00.000000",
            "operationAmount": {"amount": "75.50", "currency": {"name": "RUB"}},
            "description": "Возврат",
            "from": "Maestro 1234123412341234",
            "to": "Счет 5555666677778888"
        },
        {
            "id": 5,
            "state": "EXECUTED",
            "date": "2023-12-25T00:00:00.000000",
            "operationAmount": {"amount": "300.00", "currency": {"name": "USD"}},
            "description": "Подарок",
            "to": "Счет 1234123412341234"
        }
    ]


@pytest.fixture
def empty_transactions():
    """Фикстура с пустым списком транзакций"""
    return []


@pytest.fixture
def transactions_with_same_date():
    """Фикстура с транзакциями с одинаковыми датами"""
    return [
        {
            "id": 1,
            "state": "EXECUTED",
            "date": "2023-10-01T12:00:00.000000",
            "operationAmount": {"amount": "100.00", "currency": {"name": "USD"}}
        },
        {
            "id": 2,
            "state": "EXECUTED",
            "date": "2023-10-01T12:00:00.000000",
            "operationAmount": {"amount": "200.00", "currency": {"name": "EUR"}}
        },
        {
            "id": 3,
            "state": "EXECUTED",
            "date": "2023-10-01T08:00:00.000000",
            "operationAmount": {"amount": "300.00", "currency": {"name": "RUB"}}
        }
    ]