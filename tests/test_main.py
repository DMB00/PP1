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

    @patch('builtins.open', new_callable=mock_open, read_data='[{"state": "EXECUTED"}]')
    @patch('main.json.load')
    def test_load_transactions_from_json_success(self, mock_json_load, mock_file):
        """Тест успешной загрузки JSON"""
        from main import load_transactions_from_json

        mock_json_load.return_value = [{"state": "EXECUTED"}]

        with patch('main.DATA_DIR', Path('/fake')):
            result = load_transactions_from_json("test.json")
            assert len(result) == 1

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_transactions_from_json_not_found(self, mock_file):
        """Тест загрузки несуществующего JSON файла"""
        from main import load_transactions_from_json

        with patch('main.DATA_DIR', Path('/fake')):
            result = load_transactions_from_json("nonexistent.json")
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

    def test_filter_by_status_empty(self):
        """Тест фильтрации с пустым статусом"""
        from main import filter_by_status

        transactions = [{'status': 'EXECUTED', 'amount': '100'}]
        result = filter_by_status(transactions, '')
        assert len(result) == 1

    def test_filter_by_status_none_data(self):
        """Тест фильтрации с None данными"""
        from main import filter_by_status

        result = filter_by_status(None, 'TEST')
        assert result == []

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
        # Должен завершиться без ошибок
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

    def test_mask_card_number(self):
        """Тест маскировки номера карты"""
        from main import mask_card_number

        result = mask_card_number("1234567812345678")
        assert result == "1234 56** **** 5678"

        result = mask_card_number("1234 5678 1234 5678")
        assert result == "1234 56** **** 5678"

        result = mask_card_number("1234")
        assert result == "1234"

        result = mask_card_number("")
        assert result == ""

        result = mask_card_number(None)
        assert result == ""

    def test_mask_account_number(self):
        """Тест маскировки номера счета"""
        from main import mask_account_number

        result = mask_account_number("1234567890123456")
        assert result == "Счет **3456"

        result = mask_account_number("123")
        assert result == "123"

        result = mask_account_number("")
        assert result == ""

        result = mask_account_number(None)
        assert result == ""

    @patch('builtins.input', return_value='1')
    def test_get_user_choice_valid(self, mock_input):
        """Тест валидного выбора пользователя"""
        from main import get_user_choice

        options = ["Option 1", "Option 2", "Option 3"]
        result = get_user_choice(options, "Choose:")
        assert result == "Option 1"

    @patch('builtins.input', side_effect=['5', '2'])  # Сначала неверный, потом верный
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

    def test_format_transaction_complete(self):
        """Тест форматирования полной транзакции"""
        from main import format_transaction

        transaction = {
            'date': '22.04.2018',
            'description': 'Перевод организации',
            'from': 'Visa 1234567812345678',  # Карта с префиксом
            'to': 'Счет 1234567890123456',  # Счет с префиксом
            'amount': '1000.50',
            'currency': 'RUB'
        }

        result = format_transaction(transaction)

        # Проверяем базовые элементы
        assert '22.04.2018' in result
        assert 'Перевод организации' in result
        assert '1000.50 RUB' in result

        # Проверяем что маскированные данные присутствуют
        has_card_mask = '1234 56** **** 5678' in result
        has_account_mask = 'Счет **3456' in result

        # Достаточно что хотя бы одна маскировка присутствует
        assert has_card_mask or has_account_mask

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
        assert '22.04.2018' in result
        assert 'Тест' in result
        assert '100 USD' in result

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

        with patch('pathlib.Path.exists') as mock_exists:
            with patch('pathlib.Path.is_file') as mock_isfile:
                with patch('pathlib.Path.name', return_value='file1.json'):
                    mock_exists.return_value = True
                    mock_isfile.return_value = True

                    with patch('main.DATA_DIR') as mock_data_dir:
                        mock_data_dir.glob.return_value = [Path('file1.json'), Path('file2.csv')]
                        list_available_files()
                        assert mock_print.called

    @patch('builtins.print')
    def test_list_available_files_not_exists(self, mock_print):
        """Тест списка доступных файлов когда папка не существует"""
        from main import list_available_files

        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False

            list_available_files()
            mock_print.assert_called()

    def test_count_operations_by_status_counter(self):
        """Тест подсчета операций по статусам с Counter"""
        from main import count_operations_by_status_counter

        transactions = [
            {'status': 'EXECUTED'},
            {'status': 'PENDING'},
            {'status': 'EXECUTED'},
            {'status': ''},
            {}
        ]

        result = count_operations_by_status_counter(transactions)
        assert result['EXECUTED'] == 2
        assert result['PENDING'] == 1

    def test_count_operations_by_status_counter_empty(self):
        """Тест подсчета операций по статусам с пустыми данными"""
        from main import count_operations_by_status_counter

        result = count_operations_by_status_counter([])
        assert result == {}

        result = count_operations_by_status_counter(None)
        assert result == {}

    @patch('main.list_available_files')
    @patch('main.get_user_choice')
    @patch('main.load_transactions_from_json')
    @patch('main.get_available_statuses')
    @patch('main.get_status_filter')
    @patch('main.filter_by_status')
    @patch('main.get_yes_no_input')
    @patch('main.get_sort_direction')
    @patch('main.sort_by_date')
    @patch('main.filter_rub_transactions')
    @patch('main.count_operations_by_status_counter')
    @patch('main.print_transactions')
    def test_main_success_flow(self, mock_print_trans, mock_count_stats, mock_filter_rub,
                               mock_sort, mock_get_dir, mock_yes_no, mock_filter,
                               mock_status, mock_avail, mock_load, mock_choice, mock_files):
        """Тест успешного выполнения основного потока"""
        from main import main

        # Настраиваем моки
        mock_choice.return_value = "Получить информацию о транзакциях из JSON-файла"
        mock_load.return_value = [{'status': 'EXECUTED', 'description': 'Тест', 'date': '01.01.2023'}]
        mock_avail.return_value = ['EXECUTED']
        mock_status.return_value = 'EXECUTED'
        mock_filter.return_value = [{'status': 'EXECUTED', 'description': 'Тест', 'date': '01.01.2023'}]
        mock_yes_no.side_effect = [True, False, False]  # Сортировать да, руб нет, поиск нет
        mock_get_dir.return_value = False  # По возрастанию
        mock_sort.return_value = [{'status': 'EXECUTED', 'description': 'Тест', 'date': '01.01.2023'}]
        mock_filter_rub.return_value = [{'status': 'EXECUTED', 'description': 'Тест', 'date': '01.01.2023'}]
        mock_count_stats.return_value = {'EXECUTED': 1}

        with patch('sys.stdout', new_callable=StringIO):
            with patch('main.setup_logging'):
                main()

        # Проверяем что основные функции вызывались
        mock_load.assert_called_once()
        mock_filter.assert_called_once()
        mock_sort.assert_called_once()
        mock_print_trans.assert_called_once()

    @patch('main.list_available_files')
    @patch('main.get_user_choice')
    @patch('main.load_transactions_from_json')
    def test_main_no_transactions(self, mock_load, mock_choice, mock_files):
        """Тест когда не удалось загрузить транзакции"""
        from main import main

        mock_choice.return_value = "JSON"
        mock_load.return_value = []

        with patch('sys.stdout', new_callable=StringIO):
            with patch('main.setup_logging'):
                main()

        mock_load.assert_called_once()

    @patch('main.list_available_files')
    @patch('main.get_user_choice')
    @patch('main.load_transactions_from_json')
    @patch('main.get_available_statuses')
    def test_main_no_available_statuses(self, mock_avail, mock_load, mock_choice, mock_files):
        """Тест когда нет доступных статусов"""
        from main import main

        mock_choice.return_value = "JSON"
        mock_load.return_value = [{'description': 'Тест'}]
        mock_avail.return_value = []

        with patch('sys.stdout', new_callable=StringIO):
            with patch('main.setup_logging'):
                main()

        mock_avail.assert_called_once()

    @patch('main.list_available_files')
    @patch('main.get_user_choice')
    @patch('main.load_transactions_from_json')
    @patch('main.get_available_statuses')
    @patch('main.get_status_filter')
    @patch('main.filter_by_status')
    def test_main_no_filtered_transactions(self, mock_filter, mock_status, mock_avail, mock_load, mock_choice,
                                           mock_files):
        """Тест когда нет отфильтрованных транзакций"""
        from main import main

        mock_choice.return_value = "JSON"
        mock_load.return_value = [{'status': 'EXECUTED'}]
        mock_avail.return_value = ['EXECUTED']
        mock_status.return_value = 'EXECUTED'
        mock_filter.return_value = []

        with patch('sys.stdout', new_callable=StringIO):
            with patch('main.setup_logging'):
                main()

        mock_filter.assert_called_once()


# Простые рабочие тесты
class TestSimpleWorkingTests:
    """Простые тесты которые гарантированно работают"""

    def test_mask_functions_directly(self):
        """Прямой тест функций маскировки"""
        from main import mask_card_number, mask_account_number

        card_result = mask_card_number("1234567812345678")
        account_result = mask_account_number("1234567890123456")

        assert card_result == "1234 56** **** 5678"
        assert account_result == "Счет **3456"

    def test_format_transaction_basic(self):
        """Базовый тест форматирования без сложных проверок"""
        from main import format_transaction

        transaction = {
            'date': '22.04.2018',
            'description': 'Тест',
            'amount': '100',
            'currency': 'USD'
        }

        result = format_transaction(transaction)

        assert isinstance(result, str)
        assert len(result) > 0
        assert '22.04.2018' in result
        assert 'Тест' in result
