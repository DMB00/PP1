import pytest
import pandas as pd
import os
import tempfile
from src.financial_reader import FinancialDataReader


class TestFinancialDataReader:
    """Тесты для класса FinancialDataReader"""

    @pytest.fixture
    def reader(self):
        """Фикстура создания экземпляра reader"""
        return FinancialDataReader()

    @pytest.fixture
    def sample_csv_data(self):
        """Фикстура с тестовыми CSV данными"""
        return """id;state;date;amount;currency_name;currency_code;from;to;description
650703;EXECUTED;2023-09-05T11:30:32;16210;Sol;PEN;Счет 58803664561298323391;Счет 39745660563456619397;Перевод организации
3598919;EXECUTED;2020-12-06T23:00:58;29740;Peso;COP;Discover 3172601889670065;Discover 0720428384694643;Перевод с карты на карту
593027;CANCELED;2023-07-22T05:02:01;30368;Shilling;TZS;Visa 1959232722494097;Visa 6804119550473710;Перевод с карты на карту"""

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
            'from': ['Счет 58803664561298323391', 'Discover 3172601889670065', 'Visa 1959232722494097'],
            'to': ['Счет 39745660563456619397', 'Discover 0720428384694643', 'Visa 6804119550473710'],
            'description': ['Перевод организации', 'Перевод с карты на карту', 'Перевод с карты на карту']
        }
        return pd.DataFrame(data)

    def test_reader_initialization(self, reader):
        """Тест инициализации класса"""
        assert reader.transactions == []
        assert isinstance(reader.transactions, list)

    def test_read_csv_file_success(self, reader, sample_csv_data):
        """Тест успешного чтения CSV файла"""
        # Создаем временный CSV файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_data)
            temp_csv_path = f.name

        try:
            df = reader.read_csv_file(temp_csv_path)
            transactions = reader.process_transactions(df, 'csv')

            # Проверяем обработку
            assert len(transactions) == 3
            assert transactions[0]['source'] == 'csv'
            assert transactions[0]['id'] == 650703
            assert transactions[0]['amount'] == 16210
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
        assert transactions[1]['description'] == 'Перевод с карты на карту'

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

    def test_read_all_data_success(self, reader, sample_csv_data, sample_excel_data):
        """Тест чтения данных из обоих файлов"""
        # Создаем временные файлы
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as csv_file:
            csv_file.write(sample_csv_data)
            temp_csv_path = csv_file.name

        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as excel_file:
            temp_excel_path = excel_file.name

        try:
            # Сохраняем Excel данные
            sample_excel_data.to_excel(temp_excel_path, index=False)

            # Читаем оба файла
            transactions = reader.read_all_data(temp_csv_path, temp_excel_path)

            # Проверяем результат
            assert len(transactions) == 6  # 3 из CSV + 3 из Excel
            csv_count = sum(1 for t in transactions if t['source'] == 'csv')
            excel_count = sum(1 for t in transactions if t['source'] == 'excel')
            assert csv_count == 3
            assert excel_count == 3

        finally:
            os.unlink(temp_csv_path)
            os.unlink(temp_excel_path)

    def test_read_all_data_missing_files(self, reader):
        """Тест чтения при отсутствии файлов"""
        transactions = reader.read_all_data('nonexistent.csv', 'nonexistent.xlsx')

        # Должен вернуть пустой список
        assert transactions == []

    def test_display_transactions(self, reader, sample_excel_data, capsys):
        """Тест отображения транзакций"""
        transactions = reader.process_transactions(sample_excel_data, 'excel')
        reader.display_transactions(transactions, limit=2)

        captured = capsys.readouterr()
        output = captured.out

        # Проверяем что вывод содержит ожидаемую информацию
        assert "ФИНАНСОВЫЕ ОПЕРАЦИИ" in output
        assert "Транзакция 1" in output
        assert "Транзакция 2" in output
        assert "650703" in output  # ID первой транзакции
        assert "EXECUTED" in output  # Статус


class TestFinancialDataReaderIntegration:
    """Интеграционные тесты с реальными файлами"""

    @pytest.fixture
    def create_test_files(self):
        """Создание тестовых файлов для интеграционных тестов"""
        # CSV данные
        csv_content = """id;state;date;amount;currency_name;currency_code;from;to;description
1;EXECUTED;2023-01-01T10:00:00;1000;Dollar;USD;Card 1234;Account 5678;Test transaction 1
2;CANCELED;2023-01-02T11:00:00;2000;Euro;EUR;Card 5678;Account 9012;Test transaction 2"""

        # Excel данные
        excel_data = pd.DataFrame({
            'id': [3, 4],
            'state': ['EXECUTED', 'PENDING'],
            'date': ['2023-01-03T12:00:00Z', '2023-01-04T13:00:00Z'],
            'amount': [3000, 4000],
            'currency_name': ['Yen', 'Pound'],
            'currency_code': ['JPY', 'GBP'],
            'from': ['Card 9012', 'Card 3456'],
            'to': ['Account 3456', 'Account 7890'],
            'description': ['Test transaction 3', 'Test transaction 4']
        })

        # Сохраняем файлы
        with open('test_transactions.csv', 'w', encoding='utf-8') as f:
            f.write(csv_content)

        excel_data.to_excel('test_transactions.xlsx', index=False)

        yield

        # Убираем тестовые файлы после тестов
        if os.path.exists('test_transactions.csv'):
            os.remove('test_transactions.csv')
        if os.path.exists('test_transactions.xlsx'):
            os.remove('test_transactions.xlsx')

    def test_integration_with_real_files(self, create_test_files):
        """Интеграционный тест с реальными файлами"""
        reader = FinancialDataReader()

        transactions = reader.read_all_data(
            'test_transactions.csv',
            'test_transactions.xlsx'
        )

        assert len(transactions) == 4
        assert any(t['source'] == 'csv' for t in transactions)
        assert any(t['source'] == 'excel' for t in transactions)

        # Проверяем что все транзакции имеют правильную структуру
        for transaction in transactions:
            assert 'id' in transaction
            assert 'state' in transaction
            assert 'amount' in transaction
            assert 'currency_name' in transaction
            assert 'description' in transaction
            assert 'source' in transaction


def test_edge_cases():
    """Тесты граничных случаев"""
    reader = FinancialDataReader()

    # Пустой DataFrame
    empty_df = pd.DataFrame()
    transactions = reader.process_transactions(empty_df, 'test')
    assert transactions == []

    # DataFrame с неправильными типами данных
    wrong_types_df = pd.DataFrame({
        'id': ['not_a_number'],
        'state': [123],  # Число вместо строки
        'date': ['invalid_date'],
        'amount': ['not_a_number'],
        'currency_name': [456],
        'currency_code': [789],
        'from': [None],
        'to': [None],
        'description': [999]
    })

    transactions = reader.process_transactions(wrong_types_df, 'test')
    # Должен обработать несмотря на неправильные типы
    assert len(transactions) == 1


if __name__ == "__main__":
    # Запуск тестов без pytest
    pytest.main([__file__, "-v"])