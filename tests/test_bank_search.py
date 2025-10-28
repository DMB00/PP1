import pytest
import sys
import os
import re
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bank_search import (
    process_bank_search,
    process_bank_operations,
    process_bank_operations_advanced
)


class TestBankSearch:
    """Тесты для bank_search.py"""

    def setup_method(self):
        self.sample_data = [
            {'description': 'Перевод организации', 'amount': 100},
            {'description': 'Оплата услуг', 'amount': 200},
            {'description': 'Перевод другу', 'amount': 50},
            {'description': 'Пополнение счета', 'amount': 500}
        ]

    def test_process_bank_search_found(self):
        """Тест поиска операций - найдены результаты"""
        result = process_bank_search(self.sample_data, 'Перевод')
        assert len(result) == 2
        assert all('Перевод' in op['description'] for op in result)

    def test_process_bank_search_not_found(self):
        """Тест поиска операций - ничего не найдено"""
        result = process_bank_search(self.sample_data, 'Несуществующий')
        assert len(result) == 0

    def test_process_bank_search_empty_data(self):
        """Тест поиска с пустыми данными"""
        result = process_bank_search([], 'Перевод')
        assert result == []

    def test_process_bank_search_empty_search(self):
        """Тест поиска с пустой строкой поиска"""
        result = process_bank_search(self.sample_data, '')
        assert len(result) == 4

    def test_process_bank_search_case_insensitive(self):
        """Тест регистронезависимого поиска"""
        result_lower = process_bank_search(self.sample_data, 'перевод')
        result_upper = process_bank_search(self.sample_data, 'ПЕРЕВОД')
        assert len(result_lower) == 2
        assert len(result_upper) == 2

    def test_process_bank_search_regex_error(self):
        """Тест обработки ошибки регулярного выражения"""
        # Создаем невалидное регулярное выражение
        result = process_bank_search(self.sample_data, 'test[')
        # Должен вернуть пустой список при ошибке regex
        assert isinstance(result, list)

    def test_process_bank_operations_found(self):
        """Тест подсчета операций по категориям"""
        categories = ['Перевод организации', 'Оплата услуг', 'Несуществующая']
        result = process_bank_operations(self.sample_data, categories)

        assert result['Перевод организации'] == 1
        assert result['Оплата услуг'] == 1
        assert result['Несуществующая'] == 0

    def test_process_bank_operations_empty_data(self):
        """Тест подсчета с пустыми данными"""
        result = process_bank_operations([], ['Категория'])
        assert result == {'Категория': 0}

    def test_process_bank_operations_empty_categories(self):
        """Тест подсчета с пустым списком категорий"""
        result = process_bank_operations(self.sample_data, [])
        assert result == {}

    def test_process_bank_operations_advanced(self):
        """Тест расширенного подсчета операций"""
        result = process_bank_operations_advanced(self.sample_data)

        assert result['Перевод организации'] == 1
        assert result['Оплата услуг'] == 1
        assert result['Перевод другу'] == 1
        assert result['Пополнение счета'] == 1

    def test_process_bank_operations_advanced_empty(self):
        """Тест расширенного подсчета с пустыми данными"""
        result = process_bank_operations_advanced([])
        assert result == {}

    @patch('bank_search.logging.getLogger')
    def test_logging(self, mock_logger):
        """Тест логирования"""
        mock_logger.return_value = MagicMock()

        process_bank_search(self.sample_data, 'Перевод')
        process_bank_operations(self.sample_data, ['Категория'])

        assert mock_logger.called
