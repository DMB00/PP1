import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generators import filter_by_currency, transaction_descriptions, card_number_generator


class TestGenerators:
    """Тесты для generators.py"""

    def setup_method(self):
        self.sample_transactions = [
            {
                'operationAmount': {
                    'currency': {'code': 'USD'}
                },
                'description': 'Transaction 1'
            },
            {
                'operationAmount': {
                    'currency': {'code': 'EUR'}
                },
                'description': 'Transaction 2'
            },
            {
                'operationAmount': {
                    'currency': {'code': 'USD'}
                },
                'description': 'Transaction 3'
            }
        ]

    def test_filter_by_currency_found(self):
        """Тест фильтрации по валюте - найдены результаты"""
        generator = filter_by_currency(self.sample_transactions, 'USD')
        results = list(generator)

        assert len(results) == 2
        assert all(t['operationAmount']['currency']['code'] == 'USD' for t in results)

    def test_filter_by_currency_not_found(self):
        """Тест фильтрации по валюте - ничего не найдено"""
        generator = filter_by_currency(self.sample_transactions, 'GBP')
        results = list(generator)

        assert len(results) == 0

    def test_transaction_descriptions(self):
        """Тест генератора описаний транзакций"""
        generator = transaction_descriptions(self.sample_transactions)
        results = list(generator)

        assert results == ['Transaction 1', 'Transaction 2', 'Transaction 3']

    def test_card_number_generator_small_range(self):
        """Тест генератора номеров карт - маленький диапазон"""
        generator = card_number_generator(1, 3)
        results = list(generator)

        expected = [
            '0000 0000 0000 0001',
            '0000 0000 0000 0002',
            '0000 0000 0000 0003'
        ]
        assert results == expected

    def test_card_number_generator_single(self):
        """Тест генератора номеров карт - один номер"""
        generator = card_number_generator(1234, 1234)
        results = list(generator)

        assert results == ['0000 0000 0000 1234']

    def test_card_number_generator_format(self):
        """Тест формата номеров карт"""
        generator = card_number_generator(1234567812345678, 1234567812345678)
        results = list(generator)

        assert results == ['1234 5678 1234 5678']
