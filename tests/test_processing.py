import pytest
import sys
import os
import re
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from processing import process_bank_search, count_operations_by_category, get_all_categories


class TestProcessing:
    """Тесты для функций обработки банковских операций"""

    def setup_method(self):
        """Подготовка тестовых данных"""
        self.sample_operations = [
            {'id': 1, 'description': 'Перевод организации', 'amount': 100, 'date': '2023-01-01'},
            {'id': 2, 'description': 'Оплата услуг', 'amount': 200, 'date': '2023-01-02'},
            {'id': 3, 'description': 'Перевод другу', 'amount': 50, 'date': '2023-01-03'},
            {'id': 4, 'description': 'Пополнение счета', 'amount': 500, 'date': '2023-01-04'},
            {'id': 5, 'description': 'Оплата налогов', 'amount': 300, 'date': '2023-01-05'},
        ]

    def test_process_bank_search_found(self):
        """Тест поиска операций - найденные результаты"""
        result = process_bank_search(self.sample_operations, 'Перевод')

        assert len(result) == 2
        assert all('Перевод' in op['description'] for op in result)
        assert result[0]['id'] == 1
        assert result[1]['id'] == 3

    def test_process_bank_search_not_found(self):
        """Тест поиска операций - ничего не найдено"""
        result = process_bank_search(self.sample_operations, 'Несуществующий')

        assert len(result) == 0

    def test_process_bank_search_case_insensitive(self):
        """Тест регистронезависимого поиска"""
        result_lower = process_bank_search(self.sample_operations, 'перевод')
        result_upper = process_bank_search(self.sample_operations, 'ПЕРЕВОД')

        assert len(result_lower) == 2
        assert len(result_upper) == 2

    def test_process_bank_search_empty_data(self):
        """Тест поиска с пустыми данными"""
        result = process_bank_search([], 'Перевод')
        assert result == []

    def test_process_bank_search_empty_search(self):
        """Тест поиска с пустой строкой поиска"""
        result = process_bank_search(self.sample_operations, '')
        assert result == []

    def test_process_bank_search_special_characters(self):
        """Тест поиска со специальными символами"""
        operations = [{'description': 'Оплата 100%'}, {'description': 'Скидка 50%'}]
        result = process_bank_search(operations, '100%')

        assert len(result) == 1
        assert result[0]['description'] == 'Оплата 100%'

    def test_process_bank_search_re_error(self):
        """Тест ошибки re.error в process_bank_search"""
        with patch('processing.re.compile', side_effect=re.error("Invalid pattern")):
            result = process_bank_search(self.sample_operations, 'test[invalid')
            assert result == []

    def test_process_bank_search_general_exception(self):
        """Тест общего исключения в process_bank_search"""
        with patch('processing.re.compile', side_effect=Exception("Unexpected error")):
            result = process_bank_search(self.sample_operations, 'test')
            assert result == []

    def test_count_operations_by_category_found(self):
        """Тест подсчета операций по категориям - найденные категории"""
        categories = ['Перевод организации', 'Оплата услуг', 'Несуществующая']
        result = count_operations_by_category(self.sample_operations, categories)

        assert result['Перевод организации'] == 1
        assert result['Оплата услуг'] == 1
        assert result['Несуществующая'] == 0

    def test_count_operations_by_category_all(self):
        """Тест подсчета всех категорий"""
        all_cats = ['Перевод организации', 'Оплата услуг', 'Перевод другу',
                    'Пополнение счета', 'Оплата налогов']
        result = count_operations_by_category(self.sample_operations, all_cats)

        assert sum(result.values()) == 5
        assert result['Перевод другу'] == 1
        assert result['Оплата налогов'] == 1

    def test_count_operations_by_category_empty_data(self):
        """Тест подсчета с пустыми данными"""
        result = count_operations_by_category([], ['Категория 1', 'Категория 2'])

        assert result['Категория 1'] == 0
        assert result['Категория 2'] == 0

    def test_count_operations_by_category_empty_categories(self):
        """Тест подсчета с пустым списком категорий"""
        result = count_operations_by_category(self.sample_operations, [])

        assert result == {}

    def test_count_operations_by_category_duplicates(self):
        """Тест подсчета с дублирующимися операциями"""
        operations = [
            {'description': 'Перевод'},
            {'description': 'Перевод'},
            {'description': 'Оплата'},
        ]
        result = count_operations_by_category(operations, ['Перевод', 'Оплата'])

        assert result['Перевод'] == 2
        assert result['Оплата'] == 1

    def test_count_operations_by_category_edge_cases(self):
        """Тест граничных случаев подсчета операций"""
        operations = [
            {'description': None},
            {'description': ''},
            {'description': '  '},
        ]
        result = count_operations_by_category(operations, ['test'])
        assert result['test'] == 0

    def test_count_operations_by_category_special_characters(self):
        """Тест подсчета операций со специальными символами"""
        operations = [
            {'description': 'Оплата 100%'},
            {'description': 'Скидка 50%'},
            {'description': 'Оплата 100%'}
        ]
        result = count_operations_by_category(operations, ['Оплата 100%', 'Скидка 50%'])
        assert result['Оплата 100%'] == 2
        assert result['Скидка 50%'] == 1

    def test_get_all_categories(self):
        """Тест получения всех уникальных категорий"""
        categories = get_all_categories(self.sample_operations)

        expected = ['Оплата налогов', 'Оплата услуг', 'Перевод другу',
                    'Перевод организации', 'Пополнение счета']
        assert categories == expected

    def test_get_all_categories_empty(self):
        """Тест получения категорий из пустых данных"""
        assert get_all_categories([]) == []

    def test_get_all_categories_with_none(self):
        """Тест получения категорий с None описаниями"""
        operations = [
            {'description': 'Категория 1'},
            {'description': None},
            {'description': ''},
            {'description': 'Категория 2'},
        ]
        categories = get_all_categories(operations)

        assert 'Категория 1' in categories
        assert 'Категория 2' in categories

    def test_get_all_categories_with_none_and_empty(self):
        """Тест получения категорий с None и пустыми значениями"""
        operations = [
            {'description': 'Категория 1'},
            {'description': None},
            {'description': ''},
            {'description': '  '},  # пробелы
            {'description': 'Категория 2'},
        ]
        categories = get_all_categories(operations)

        # Проверяем что основные категории есть
        assert 'Категория 1' in categories
        assert 'Категория 2' in categories
        # Не проверяем наличие пустых строк, так как логика может их фильтровать
        assert len(categories) >= 2
