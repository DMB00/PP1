import pytest
import pandas as pd
import os
import tempfile
from src.financial_reader import FinancialDataReader, display_transactions


class TestFinancialDataReader:
    """Тесты для класса FinancialDataReader"""

    @pytest.fixture
    def reader(self):
        """Фикстура создания экземпляра reader"""
        return FinancialDataReader()

    @pytest.fixture
    def sample_csv_data(self):
        """Фикстура с тестовыми CSV данными в правильной кодировке"""
        return """id;state;date;amount;currency_name;currency_code;from;to;description
650703;EXECUTED;2023-09-05T11:30:32;16210;Sol;PEN;Account 58803664561298323391;Account 39745660563456619397;Transfer
3598919;EXECUTED;2020-12-06T23:00:58;29740;Peso;COP;Discover 3172601889670065;Discover 0720428384694643;Card transfer
593027;CANCELED;2023-07-22T05:02:01;30368;Shilling;TZS;Visa 1959232722494097;Visa 6804119550473710;Card transfer"""

    @pytest.fixture
    def sample_excel_data(self):
        """Фикстура с тестовыми Excel данными"""
        data = {
            'id': [650703, 3598919, 593027],
            'state': ['EXECUTED', 'EXECUTED', 'CANCELED'],
            'date': ['2023-09-05T11:30:32Z', '2020-12-06T23:00:58Z', '2023-07-22T05:02:01Z'],
            'amount': [16210, 29740, 30368],
            'currency_name': ['Sol', 'Peso', 'Shilling'],
            'currency_code': ['PEN', 'COP', 'TZS'],
            'from': ['Account 58803664561298323391', 'Discover 3172601889670065', 'Visa 1959232722494097'],
            'to': ['Account 39745660563456619397', 'Discover 0720428384694643', 'Visa 6804119550473710'],
            'description': ['Organization transfer', 'Card to card transfer', 'Card to card transfer']
        }
        return pd.DataFrame(data)

    def test_reader_initialization(self, reader):
        """Тест инициализации класса"""
        assert reader.transactions == []
        assert isinstance(reader.transactions, list)

    def test_read_csv_file_success(self, reader, sample_csv_data):
        """Тест успешного чтения CSV файла"""
        # Создаем временный CSV файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(sample_csv_data)
            temp_csv_path = f.name

        try:
            # Читаем файл
            result = reader.read_csv_file(temp_csv_path)

            # Проверяем результат
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3
            assert list(result.columns) == ['id', 'state', 'date', 'amount', 'currency_name',
                                            'currency_code', 'from', 'to', 'description']
            assert result.iloc[0]['id'] == 650703
            assert result.iloc[1]['state'] == 'EXECUTED'
        finally:
            # Удаляем временный файл
            os.unlink(temp_csv_path)

    def test_read_csv_file_not_found(self, reader):
        """Тест чтения несуществующего CSV файла"""
        with pytest.raises(Exception):
            reader.read_csv_file('nonexistent_file.csv')

    def test_read_excel_file_success(self, reader, sample_excel_data):
        """Тест успешного чтения Excel файла"""
        # Создаем временный Excel файл
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_excel_path = f.name

        try:
            # Сохраняем данные в Excel
            sample_excel_data.to_excel(temp_excel_path, index=False)

            # Читаем файл
            result = reader.read_excel_file(temp_excel_path)

            # Проверяем результат
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3
            assert result.iloc[0]['id'] == 650703
            assert result.iloc[2]['state'] == 'CANCELED'
        finally:
            # Удаляем временный файл
            os.unlink(temp_excel_path)

    def test_process_transactions_csv(self, reader, sample_csv_data):
        """Тест обработки CSV транзакций"""
        # Создаем временный файл и читаем его
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(sample_csv_data)
            temp_csv_path = f.name

        try:
            df = reader.read_csv_file(temp_csv_path)
            transactions = reader.process_transactions(df, 'csv')

            # Проверяем обработку
            assert len(transactions) == 3
            assert transactions[0]['source'] == 'csv'
            assert transactions[0]['id'] == 650703
            assert transactions[0]['amount'] == 16210.0
            assert transactions[0]['currency_name'] == 'Sol'
            assert 'from_account' in transactions[0]
            assert 'to_account' in transactions[0]
        finally:
            os.unlink(temp_csv_path)

    def test_process_transactions_excel(self, reader, sample_excel_data):
        """Тест обработки Excel транзакций"""
        transactions = reader.process_transactions(sample_excel_data, 'excel')

        assert len(transactions) == 3
        assert transactions[1]['source'] == 'excel'
        assert transactions[1]['id'] == 3598919
        assert transactions[1]['description'] == 'Card to card transfer'

    def test_process_transactions_missing_columns(self, reader):
        """Тест обработки данных с отсутствующими колонками"""
        # Создаем DataFrame с отсутствующими колонками
        incomplete_data = pd.DataFrame({
            'id': [1, 2],
            'state': ['EXECUTED', 'CANCELED'],
            # Отсутствуют обязательные колонки
        })

        transactions = reader.process_transactions(incomplete_data, 'test')

        # Должен вернуть пустой список из-за ошибок
        assert len(transactions) == 0


def test_display_transactions(capsys):
    """Тест отображения транзакций"""
    transactions = [
        {
            'id': 1,
            'state': 'EXECUTED',
            'date': '2023-01-01',
            'amount': 1000.0,
            'currency_name': 'RUB',
            'currency_code': 'RUB',
            'from_account': 'Account 123',
            'to_account': 'Account 456',
            'description': 'Test transaction',
            'source': 'test'
        }
    ]

    display_transactions(transactions, limit=1)
    captured = capsys.readouterr()
    output = captured.out

    assert "ФИНАНСОВЫЕ ОПЕРАЦИИ" in output
    assert "Транзакция 1" in output
    assert "Test transaction" in output


def test_edge_cases():
    """Тест граничных случаев"""
    reader = FinancialDataReader()

    # Пустой DataFrame
    empty_df = pd.DataFrame()
    transactions = reader.process_transactions(empty_df, 'test')
    assert transactions == []
