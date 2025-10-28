import pytest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestMainComprehensive:
    """Комплексные тесты для main.py"""

    def test_setup_logging(self):
        """Тест настройки логирования"""
        from main import setup_logging

        with patch('main.logging.basicConfig') as mock_basic_config:
            with patch('pathlib.Path.mkdir') as mock_mkdir:
                setup_logging()
                mock_mkdir.assert_called_once_with(exist_ok=True)
                mock_basic_config.assert_called_once()

    def test_mask_card_number(self):
        """Тест маскировки номера карты"""
        from main import mask_card_number

        # Тест с полным номером
        result = mask_card_number("1234567812345678")
        assert result == "1234 56** **** 5678"

        # Тест с номером с пробелами
        result = mask_card_number("1234 5678 1234 5678")
        assert result == "1234 56** **** 5678"

        # Тест с коротким номером
        result = mask_card_number("1234")
        assert result == "1234"

        # Тест с пустой строкой
        result = mask_card_number("")
        assert result == ""

        # Тест с None
        result = mask_card_number(None)
        assert result == ""

        # Тест с названием карты
        result = mask_card_number("Visa Platinum 1234567812345678")
        assert "1234 56** **** 5678" in result

    def test_mask_account_number(self):
        """Тест маскировки номера счета"""
        from main import mask_account_number

        # Тест с полным номером
        result = mask_account_number("1234567890123456")
        assert result == "Счет **3456"

        # Тест с коротким номером
        result = mask_account_number("123")
        assert result == "123"

        # Тест с пустой строкой
        result = mask_account_number("")
        assert result == ""

        # Тест с None
        result = mask_account_number(None)
        assert result == ""

        # Тест с префиксом счета
        result = mask_account_number("Счет 1234567890123456")
        assert "**3456" in result

    def test_transform_json_transaction_valid(self):
        """Тест преобразования валидной JSON транзакции"""
        from main import transform_json_transaction

        transaction = {
            "id": 1,
            "date": "2018-04-22T17:01:46.885252",
            "description": "Перевод организации",
            "from": "Счет 1234567890123456",
            "to": "Счет 9876543210987654",
            "operationAmount": {
                "amount": "1000.50",
                "currency": {"name": "RUB"}
            },
            "state": "EXECUTED"
        }

        result = transform_json_transaction(transaction)

        assert result["date"] == "22.04.2018"
        assert result["amount"] == "1000.50"
        assert result["currency"] == "RUB"
        assert result["status"] == "EXECUTED"
        assert result["description"] == "Перевод организации"

    def test_transform_json_transaction_invalid_date(self):
        """Тест преобразования с невалидной датой"""
        from main import transform_json_transaction

        transaction = {
            "date": "invalid-date",
            "operationAmount": {"amount": "100", "currency": {"name": "RUB"}},
            "state": "EXECUTED"
        }

        result = transform_json_transaction(transaction)
        assert result["date"] == "invalid-date"

    def test_transform_json_transaction_empty(self):
        """Тест преобразования пустой транзакции"""
        from main import transform_json_transaction

        result = transform_json_transaction({})
        assert result == {}

        result = transform_json_transaction(None)
        assert result == {}

    def test_transform_csv_transaction_dict(self):
        """Тест преобразования CSV транзакции (dict)"""
        from main import transform_csv_transaction

        row = {
            'id': '1',
            'date': '2020-06-07T11:11:36Z',
            'description': 'Оплата услуг',
            'from': 'Card 1234567812345678',
            'to': 'Счет 8765432187654321',
            'amount': '500.75',
            'currency_name': 'RUB',
            'status': 'COMPLETED'
        }

        result = transform_csv_transaction(row)
        assert result["date"] == "07.06.2020"
        assert result["currency"] == "RUB"
        assert result["status"] == "COMPLETED"

    def test_transform_csv_transaction_list(self):
        """Тест преобразования CSV транзакции (list)"""
        from main import transform_csv_transaction

        row = ['1', 'EXECUTED', '2020-06-07T11:11:36Z', '100', 'USD', 'Card 1234', 'Card 5678', 'Перевод другу']

        result = transform_csv_transaction(row)
        assert result["date"] == "07.06.2020"
        assert result["status"] == "EXECUTED"
        assert result["currency"] == "USD"

    def test_transform_csv_transaction_edge_cases(self):
        """Тест преобразования CSV транзакций - граничные случаи"""
        from main import transform_csv_transaction

        # Короткий список
        result = transform_csv_transaction(['1', 'EXECUTED'])
        assert result["id"] == "1"
        assert result["status"] == "EXECUTED"

        # Пустой список
        result = transform_csv_transaction([])
        assert result == {}

        # None
        result = transform_csv_transaction(None)
        assert result == {}

    @patch('main.json.load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.glob')
    def test_load_transactions_from_json_success(self, mock_glob, mock_file, mock_json_load):
        """Тест успешной загрузки JSON"""
        from main import load_transactions_from_json

        mock_glob.return_value = [Path('/fake/operations.json')]
        mock_json_load.return_value = [{"state": "EXECUTED", "date": "2020-01-01T00:00:00Z"}]

        with patch('main.DATA_DIR', Path('/fake')):
            result = load_transactions_from_json()
            assert isinstance(result, list)

    @patch('pathlib.Path.glob')
    def test_load_transactions_from_json_not_found(self, mock_glob):
        """Тест загрузки несуществующего JSON файла"""
        from main import load_transactions_from_json

        mock_glob.return_value = []  # Нет файлов

        with patch('main.DATA_DIR', Path('/fake')):
            result = load_transactions_from_json()
            assert result == []

    @patch('main.csv.DictReader')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.glob')
    def test_load_transactions_from_csv_success(self, mock_glob, mock_file, mock_csv_reader):
        """Тест успешной загрузки CSV"""
        from main import load_transactions_from_csv

        mock_glob.return_value = [Path('/fake/transactions.csv')]
        mock_csv_reader.return_value = [
            {'id': '1', 'date': '2020-01-01T00:00:00Z', 'status': 'EXECUTED'}
        ]

        with patch('main.DATA_DIR', Path('/fake')):
            result = load_transactions_from_csv()
            assert isinstance(result, list)

    @patch('pathlib.Path.glob')
    def test_load_transactions_from_csv_not_found(self, mock_glob):
        """Тест загрузки несуществующего CSV файла"""
        from main import load_transactions_from_csv

        mock_glob.return_value = []

        with patch('main.DATA_DIR', Path('/fake')):
            result = load_transactions_from_csv()
            assert result == []

    @patch('main.openpyxl.load_workbook')
    @patch('pathlib.Path.glob')
    def test_load_transactions_from_xlsx_success(self, mock_glob, mock_load_workbook):
        """Тест успешной загрузки XLSX"""
        from main import load_transactions_from_xlsx

        mock_glob.return_value = [Path('/fake/transactions.xlsx')]
        mock_workbook = MagicMock()
        mock_sheet = MagicMock()
        mock_load_workbook.return_value = mock_workbook
        mock_workbook.active = mock_sheet

        mock_sheet.__getitem__.return_value = [MagicMock(value='date'), MagicMock(value='status')]
        mock_sheet.iter_rows.return_value = []

        with patch('main.DATA_DIR', Path('/fake')):
            result = load_transactions_from_xlsx()
            assert isinstance(result, list)

    @patch('pathlib.Path.glob')
    def test_load_transactions_from_xlsx_not_found(self, mock_glob):
        """Тест загрузки несуществующего XLSX файла"""
        from main import load_transactions_from_xlsx

        mock_glob.return_value = []

        with patch('main.DATA_DIR', Path('/fake')):
            result = load_transactions_from_xlsx()
            assert result == []

    def test_filter_by_status(self):
        """Тест фильтрации по статусу"""
        from main import filter_by_status

        transactions = [
            {'status': 'EXECUTED', 'amount': '100'},
            {'status': 'PENDING', 'amount': '200'},
            {'status': 'EXECUTED', 'amount': '300'}
        ]

        result = filter_by_status(transactions, 'EXECUTED')
        assert len(result) == 2
        assert all(t['status'] == 'EXECUTED' for t in result)

    def test_filter_by_status_none_data(self):
        """Тест фильтрации с None данными"""
        from main import filter_by_status

        result = filter_by_status(None, 'TEST')
        assert result == []

    def test_filter_by_status_no_status(self):
        """Тест фильтрации транзакций без статуса"""
        from main import filter_by_status

        transactions = [
            {'amount': '100'},  # Нет статуса
            {'status': 'EXECUTED', 'amount': '200'}
        ]

        result = filter_by_status(transactions, 'EXECUTED')
        assert len(result) == 1

    def test_sort_by_date(self):
        """Тест сортировки по дате"""
        from main import sort_by_date

        transactions = [
            {'date': '15.05.2020'},
            {'date': '10.01.2020'},
            {'date': '20.12.2020'}
        ]

        result_asc = sort_by_date(transactions, reverse=False)
        dates_asc = [t['date'] for t in result_asc]
        assert dates_asc == ['10.01.2020', '15.05.2020', '20.12.2020']

        result_desc = sort_by_date(transactions, reverse=True)
        dates_desc = [t['date'] for t in result_desc]
        assert dates_desc == ['20.12.2020', '15.05.2020', '10.01.2020']

    def test_sort_by_date_invalid_dates(self):
        """Тест сортировки с невалидными датами"""
        from main import sort_by_date

        transactions = [
            {'date': 'invalid-date'},
            {'date': '15.05.2020'},
            {'date': ''}
        ]

        result = sort_by_date(transactions)
        assert len(result) == 3

    def test_sort_by_date_none_data(self):
        """Тест сортировки с None данными"""
        from main import sort_by_date

        result = sort_by_date(None)
        assert result == []

    def test_filter_rub_transactions(self):
        """Тест фильтрации рублевых транзакций"""
        from main import filter_rub_transactions

        transactions = [
            {'currency': 'RUB', 'amount': '100'},
            {'currency': 'USD', 'amount': '200'},
            {'currency': 'RUB', 'amount': '300'}
        ]

        result = filter_rub_transactions(transactions)
        assert len(result) == 2
        assert all(t['currency'] == 'RUB' for t in result)

    def test_filter_rub_transactions_various_formats(self):
        """Тест фильтрации рублевых транзакций в разных форматах"""
        from main import filter_rub_transactions

        transactions = [
            {'currency': 'RUB', 'amount': '100'},
            {'currency': 'руб', 'amount': '200'},
            {'currency': 'RUR', 'amount': '300'},
            {'currency': 'USD', 'amount': '400'}
        ]

        result = filter_rub_transactions(transactions)
        assert len(result) == 3

    def test_filter_rub_transactions_none_data(self):
        """Тест фильтрации рублевых транзакций с None данными"""
        from main import filter_rub_transactions

        result = filter_rub_transactions(None)
        assert result == []

    def test_filter_by_description(self):
        """Тест фильтрации по описанию"""
        from main import filter_by_description

        transactions = [
            {'description': 'Перевод организации', 'amount': '100'},
            {'description': 'Оплата услуг', 'amount': '200'},
            {'description': 'Перевод другу', 'amount': '300'}
        ]

        result = filter_by_description(transactions, 'перевод')
        assert len(result) == 2
        assert all('перевод' in t['description'].lower() for t in result)

    def test_filter_by_description_no_match(self):
        """Тест фильтрации без совпадений"""
        from main import filter_by_description

        transactions = [{'description': 'Тест', 'amount': '100'}]
        result = filter_by_description(transactions, 'неттакого')
        assert len(result) == 0

    def test_get_available_statuses(self):
        """Тест получения доступных статусов"""
        from main import get_available_statuses

        transactions = [
            {'status': 'EXECUTED'},
            {'status': 'PENDING'},
            {'status': 'EXECUTED'},
            {'status': ''},
            {}
        ]

        result = get_available_statuses(transactions)
        assert 'EXECUTED' in result
        assert 'PENDING' in result
        assert len(result) == 2

    def test_get_available_statuses_empty(self):
        """Тест получения статусов из пустых данных"""
        from main import get_available_statuses

        result = get_available_statuses([])
        assert result == []

        result = get_available_statuses(None)
        assert result == []

    def test_count_operations_by_status(self):
        """Тест подсчета операций по статусам"""
        from main import count_operations_by_status

        transactions = [
            {'status': 'EXECUTED'},
            {'status': 'PENDING'},
            {'status': 'EXECUTED'},
            {'status': ''},
            {}
        ]

        result = count_operations_by_status(transactions)
        assert result['EXECUTED'] == 2
        assert result['PENDING'] == 1

    def test_count_operations_by_status_empty(self):
        """Тест подсчета операций по статусам с пустыми данными"""
        from main import count_operations_by_status

        result = count_operations_by_status([])
        assert result == {}

        result = count_operations_by_status(None)
        assert result == {}

    def test_format_transaction_minimal(self):
        """Тест форматирования минимальной транзакции"""
        from main import format_transaction

        transaction = {
            'date': '22.04.2018',
            'description': 'Тест',
            'amount': '100',
            'currency': 'USD'
        }

        result = format_transaction(transaction)
        assert '22.04.2018 Тест' in result
        assert '100 USD' in result

    def test_format_transaction_only_from(self):
        """Тест форматирования транзакции только с отправителем"""
        from main import format_transaction

        transaction = {
            'date': '22.04.2018',
            'description': 'Тест',
            'from': 'Card 1234567812345678',
            'amount': '100',
            'currency': 'USD'
        }

        result = format_transaction(transaction)
        assert '1234 56** **** 5678' in result

    def test_format_transaction_only_to(self):
        """Тест форматирования транзакции только с получателем"""
        from main import format_transaction

        transaction = {
            'date': '22.04.2018',
            'description': 'Тест',
            'to': 'Счет 1234567890123456',
            'amount': '100',
            'currency': 'USD'
        }

        result = format_transaction(transaction)
        assert 'Счет **3456' in result

    @patch('builtins.print')
    def test_print_transactions_with_data(self, mock_print):
        """Тест вывода транзакций с данными"""
        from main import print_transactions

        transactions = [{
            'date': '22.04.2018',
            'description': 'Тест',
            'amount': '100',
            'currency': 'USD'
        }]

        print_transactions(transactions)
        assert mock_print.called

    @patch('builtins.print')
    def test_print_transactions_empty(self, mock_print):
        """Тест вывода пустых транзакций"""
        from main import print_transactions

        print_transactions([])
        mock_print.assert_called_with("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")

    @patch('builtins.print')
    def test_list_available_files_exists(self, mock_print):
        """Тест списка доступных файлов когда папка существует"""
        from main import list_available_files

        with patch('main.DATA_DIR') as mock_data_dir:
            mock_data_dir.exists.return_value = True
            mock_data_dir.glob.return_value = [
                MagicMock(suffix='.json', name='file1.json'),
                MagicMock(suffix='.csv', name='file2.csv')
            ]

            list_available_files()
            assert mock_print.called

    @patch('builtins.print')
    def test_list_available_files_not_exists(self, mock_print):
        """Тест списка доступных файлов когда папка не существует"""
        from main import list_available_files

        with patch('main.DATA_DIR') as mock_data_dir:
            mock_data_dir.exists.return_value = False
            mock_data_dir.__str__.return_value = '/fake/path'

            list_available_files()
            mock_print.assert_called()

    @patch('builtins.input', return_value='1')
    def test_get_user_choice_valid(self, mock_input):
        """Тест валидного выбора пользователя"""
        from main import get_user_choice

        options = ["Option 1", "Option 2", "Option 3"]
        result = get_user_choice(options, "Choose:")
        assert result == "Option 1"

    @patch('builtins.input', side_effect=['5', '2'])
    def test_get_user_choice_invalid_then_valid(self, mock_input):
        """Тест неверного затем верного выбора"""
        from main import get_user_choice

        options = ["Option 1", "Option 2", "Option 3"]
        result = get_user_choice(options, "Choose:")
        assert result == "Option 2"

    @patch('builtins.input', return_value='да')
    def test_get_yes_no_input_yes(self, mock_input):
        """Тест ввода Да"""
        from main import get_yes_no_input

        result = get_yes_no_input("Continue?")
        assert result is True

    @patch('builtins.input', return_value='нет')
    def test_get_yes_no_input_no(self, mock_input):
        """Тест ввода Нет"""
        from main import get_yes_no_input

        result = get_yes_no_input("Continue?")
        assert result is False

    @patch('builtins.input', return_value='по возрастанию')
    def test_get_sort_direction_asc(self, mock_input):
        """Тест выбора сортировки по возрастанию"""
        from main import get_sort_direction

        result = get_sort_direction()
        assert result is False

    @patch('builtins.input', return_value='по убыванию')
    def test_get_sort_direction_desc(self, mock_input):
        """Тест выбора сортировки по убыванию"""
        from main import get_sort_direction

        result = get_sort_direction()
        assert result is True

    @patch('builtins.input', return_value='test')
    def test_get_search_word(self, mock_input):
        """Тест получения слова для поиска"""
        from main import get_search_word

        result = get_search_word()
        assert result == 'test'

    @patch('builtins.input', return_value='EXECUTED')
    def test_get_status_filter(self, mock_input):
        """Тест получения статуса для фильтрации"""
        from main import get_status_filter

        available_statuses = ['EXECUTED', 'PENDING']
        result = get_status_filter(available_statuses)
        assert result == 'EXECUTED'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
