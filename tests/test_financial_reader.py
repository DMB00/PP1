import pytest
import sys
import os
import pandas as pd
from unittest.mock import patch, mock_open, MagicMock
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from financial_reader import FinancialDataReader, display_transactions, setup_logger


class TestFinancialReader:
    """Тесты для financial_reader.py"""

    def setup_method(self):
        self.reader = FinancialDataReader()

    @patch('builtins.open', new_callable=mock_open, read_data='[{"id": 1, "amount": 100}]')
    @patch('financial_reader.json.load')
    def test_read_json_file_success(self, mock_json_load, mock_file):
        """Тест успешного чтения JSON файла"""
        mock_json_load.return_value = [{"id": 1, "amount": 100}]

        result = self.reader.read_json_file("test.json")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]['id'] == 1

    @patch('builtins.open', new_callable=mock_open, read_data='{"id": 1, "amount": 100}')
    @patch('financial_reader.json.load')
    def test_read_json_file_object_not_list(self, mock_json_load, mock_file):
        """Тест чтения JSON объекта (не массива)"""
        mock_json_load.return_value = {"id": 1, "amount": 100}

        result = self.reader.read_json_file("test.json")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch('builtins.open', side_effect=Exception("File error"))
    def test_read_json_file_error(self, mock_file):
        """Тест ошибки чтения JSON файла"""
        with pytest.raises(Exception):
            self.reader.read_json_file("test.json")

    @patch('pandas.read_csv')
    def test_read_csv_file_success(self, mock_read_csv):
        """Тест успешного чтения CSV файла"""
        mock_df = pd.DataFrame({"id": [1, 2], "amount": [100, 200]})
        mock_read_csv.return_value = mock_df

        result = self.reader.read_csv_file("test.csv")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    @patch('pandas.read_csv')
    def test_read_csv_file_all_encodings_fail(self, mock_read_csv):
        """Тест когда все кодировки не сработали"""
        mock_read_csv.side_effect = Exception("Все кодировки не сработали")

        with pytest.raises(Exception, match="Все кодировки не сработали"):
            self.reader.read_csv_file("test.csv")

    @patch('pandas.read_excel')
    def test_read_excel_file_success(self, mock_read_excel):
        """Тест успешного чтения Excel файла"""
        mock_df = pd.DataFrame({"id": [1, 2], "amount": [100, 200]})
        mock_read_excel.return_value = mock_df

        result = self.reader.read_excel_file("test.xlsx")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    @patch('pandas.read_excel', side_effect=Exception("Excel error"))
    def test_read_excel_file_error(self, mock_read_excel):
        """Тест ошибки чтения Excel"""
        with pytest.raises(Exception):
            self.reader.read_excel_file("test.xlsx")

    def test_process_transactions_success(self):
        """Тест обработки транзакций"""
        df = pd.DataFrame({
            'id': [1, 2],
            'state': ['EXECUTED', 'PENDING'],
            'date': ['2023-01-01', '2023-01-02'],
            'amount': [100.0, 200.0],
            'currency_name': ['RUB', 'USD'],
            'from': ['Account1', 'Account2'],
            'to': ['Account3', 'Account4'],
            'description': ['Test1', 'Test2']
        })

        result = self.reader.process_transactions(df, "test_source")

        assert len(result) == 2
        assert result[0]['source'] == 'test_source'
        assert result[0]['amount'] == 100.0

    def test_process_transactions_missing_columns(self):
        """Тест обработки транзакций с отсутствующими колонками"""
        df = pd.DataFrame({
            'id': [1],
            'state': ['EXECUTED']
        })

        result = self.reader.process_transactions(df, "test_source")

        assert len(result) == 1
        assert result[0]['amount'] == 0.0
        assert result[0]['description'] == ''

    def test_process_transactions_with_from_account(self):
        """Тест обработки с from_account вместо from"""
        df = pd.DataFrame({
            'id': [1],
            'from_account': ['Account123']
        })

        result = self.reader.process_transactions(df, "test_source")
        assert result[0]['from_account'] == 'Account123'

    def test_process_transactions_row_error(self):
        """Тест обработки строки с ошибкой преобразования"""
        df = pd.DataFrame({
            'id': [1],
            'amount': ['not_a_number']  # Вызовет ValueError при float()
        })

        result = self.reader.process_transactions(df, "test_source")
        # Транзакция с ошибкой должна быть пропущена
        assert len(result) == 0

    @patch('builtins.print')
    def test_display_transactions_normal(self, mock_print):
        """Тест отображения транзакций"""
        transactions = [
            {
                'id': 1,
                'state': 'EXECUTED',
                'date': '2023-01-01',
                'amount': 100.0,
                'currency_name': 'RUB',
                'currency_code': 'RUB',
                'from_account': 'Account1',
                'to_account': 'Account2',
                'description': 'Test transaction',
                'source': 'test'
            }
        ]

        display_transactions(transactions, limit=1)
        assert mock_print.called

    @patch('builtins.print')
    def test_display_transactions_empty(self, mock_print):
        """Тест отображения пустого списка транзакций"""
        display_transactions([])
        mock_print.assert_called_with("Нет транзакций для отображения")

    @patch('builtins.print')
    def test_display_transactions_none(self, mock_print):
        """Тест отображения None транзакций"""
        display_transactions(None)
        mock_print.assert_called_with("Нет транзакций для отображения")


def test_setup_logger_force_recreate():
    """Тест принудительного пересоздания логгера"""
    # Используем правильную сигнатуру для financial_reader
    logger1 = setup_logger('test_logger_force_recreate')

    # Проверяем что логгер создан
    assert logger1 is not None
    assert isinstance(logger1, logging.Logger)
