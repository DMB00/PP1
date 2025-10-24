import pytest
from src.bank_search import process_bank_operations


class TestBankOperations:
    """Тесты для функций подсчета операций по категориям"""

    def test_process_bank_operations_basic(self):
        """Тест базового подсчета операций по категориям"""
        operations_data = [
            {
                'id': 1,
                'description': 'Перевод организации',
            },
            {
                'id': 2,
                'description': 'Перевод с карты на карту',
            },
            {
                'id': 3,
                'description': 'Открытие вклада',
            },
            {
                'id': 4,
                'description': 'Оплата услуг',
            },
        ]

        categories = ['Перевод', 'Вклад', 'Оплата']
        result = process_bank_operations(operations_data, categories)

        expected = {
            'Перевод': 2,  # ID 1, 2
            'Вклад': 1,  # ID 3
            'Оплата': 1  # ID 4
        }

        assert result == expected

    def test_process_bank_operations_case_insensitive(self):
        """Тест подсчета операций без учета регистра"""
        operations_data = [
            {'id': 1, 'description': 'Перевод организации'},
            {'id': 2, 'description': 'оплата услуг'},
            {'id': 3, 'description': 'ОТКРЫТИЕ ВКЛАДА'},
        ]

        categories = ['перевод', 'ОПЛАТА', 'Вклад']
        result = process_bank_operations(operations_data, categories)

        expected = {
            'перевод': 1,
            'ОПЛАТА': 1,
            'Вклад': 1
        }

        assert result == expected

    def test_process_bank_operations_no_matches(self):
        """Тест подсчета операций без совпадений"""
        operations_data = [
            {'id': 1, 'description': 'Перевод организации'},
        ]

        categories = ['НесуществующаяКатегория', 'ДругаяКатегория']
        result = process_bank_operations(operations_data, categories)

        expected = {
            'НесуществующаяКатегория': 0,
            'ДругаяКатегория': 0
        }

        assert result == expected

    def test_process_bank_operations_empty_data(self):
        """Тест подсчета операций с пустыми данными"""
        categories = ['Перевод', 'Оплата']
        result = process_bank_operations([], categories)

        assert result == {'Перевод': 0, 'Оплата': 0}

    def test_process_bank_operations_empty_categories(self):
        """Тест подсчета операций с пустым списком категорий"""
        operations_data = [
            {'id': 1, 'description': 'Перевод организации'},
        ]

        result = process_bank_operations(operations_data, [])
        assert result == {}

    def test_process_bank_operations_none_data(self):
        """Тест подсчета операций с None данными"""
        result = process_bank_operations(None, ['Перевод'])
        assert result == {}

    def test_process_bank_operations_none_categories(self):
        """Тест подсчета операций с None категориями"""
        operations_data = [
            {'id': 1, 'description': 'Перевод организации'},
        ]

        result = process_bank_operations(operations_data, None)
        assert result == {}

    def test_process_bank_operations_without_description(self):
        """Тест с операциями без поля description"""
        operations_data = [
            {'id': 1, 'description': 'Перевод'},
            {'id': 2, 'description': ''},  # Пустое описание
            {'id': 3},  # Нет поля description
            {'id': 4, 'description': 'Оплата'},
        ]

        categories = ['Перевод', 'Оплата']
        result = process_bank_operations(operations_data, categories)

        expected = {
            'Перевод': 1,  # Только ID 1
            'Оплата': 1  # Только ID 4
        }

        assert result == expected


def test_english_categories():
    """Тест с английскими категориями"""
    operations_data = [
        {'id': 1, 'description': 'Bank transfer to account'},
        {'id': 2, 'description': 'Cash withdrawal from ATM'},
        {'id': 3, 'description': 'Online payment for services'},
    ]

    categories = ['transfer', 'withdrawal', 'payment']
    result = process_bank_operations(operations_data, categories)

    expected = {
        'transfer': 1,
        'withdrawal': 1,
        'payment': 1
    }

    assert result == expected


def test_special_characters():
    """Тест специальных символов"""
    operations_data = [
        {'id': 1, 'description': 'Payment (invoice #123)'},
        {'id': 2, 'description': 'Regular payment'},
    ]

    categories = ['payment', 'invoice']
    result = process_bank_operations(operations_data, categories)

    assert result['payment'] == 2
    assert result['invoice'] == 1


def test_multiple_categories_in_one_description():
    """Тест когда в одном описании несколько категорий - ИСПРАВЛЕННЫЙ"""
    operations_data = [
        {'id': 1, 'description': 'Перевод и оплата услуг'},  # Содержит "перевод" и "оплата"
        {'id': 2, 'description': 'Вклад с пополнением'},  # Содержит "вклад" и "пополнение"
    ]

    categories = ['Перевод', 'Оплата', 'Вклад', 'Пополнение']
    result = process_bank_operations(operations_data, categories)

    # Одна операция может учитываться в нескольких категориях
    assert result['Перевод'] == 1  # "перевод" в ID 1
    assert result['Оплата'] == 1  # "оплата" в ID 1
    assert result['Вклад'] == 1  # "вклад" в ID 2
    assert result['Пополнение'] == 1  # "пополнение" в ID 2


def test_partial_matches():
    """Тест частичных совпадений"""
    operations_data = [
        {'id': 1, 'description': 'Межбанковский перевод'},  # Содержит "перевод"
        {'id': 2, 'description': 'Переводной документ'},  # Содержит "перевод"
        {'id': 3, 'description': 'Перевод'},  # Точное совпадение
    ]

    categories = ['Перевод']
    result = process_bank_operations(operations_data, categories)

    # Все три операции содержат "перевод"
    assert result['Перевод'] == 3


def test_complex_scenario():
    """Тест сложного сценария"""
    operations_data = [
        {'id': 1, 'description': 'Зарплатный перевод'},
        {'id': 2, 'description': 'Оплата коммунальных услуг'},
        {'id': 3, 'description': 'Пополнение мобильного счета'},
        {'id': 4, 'description': 'Перевод между счетами'},
        {'id': 5, 'description': 'Оплата интернета'},
        {'id': 6, 'description': 'Бонусное пополнение'},
    ]

    categories = ['Перевод', 'Оплата', 'Пополнение']
    result = process_bank_operations(operations_data, categories)

    expected = {
        'Перевод': 2,  # ID 1, 4
        'Оплата': 2,  # ID 2, 5
        'Пополнение': 2  # ID 3, 6
    }

    assert result == expected
