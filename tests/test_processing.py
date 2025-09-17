import pytest
from src.processing import filter_by_state, sort_by_date


class TestProcessing:
    """Тесты для модуля processing"""

    def test_filter_by_state_executed(self, sample_transactions):
        """Тест фильтрации по статусу EXECUTED"""
        result = filter_by_state(sample_transactions, "EXECUTED")
        assert len(result) == 3
        assert all(item["state"] == "EXECUTED" for item in result)

    def test_filter_by_state_pending(self, sample_transactions):
        """Тест фильтрации по статусу PENDING"""
        result = filter_by_state(sample_transactions, "PENDING")
        assert len(result) == 1
        assert all(item["state"] == "PENDING" for item in result)

    def test_filter_by_state_canceled(self, sample_transactions):
        """Тест фильтрации по статусу CANCELED"""
        result = filter_by_state(sample_transactions, "CANCELED")
        assert len(result) == 1
        assert all(item["state"] == "CANCELED" for item in result)

    def test_filter_by_state_nonexistent(self, sample_transactions):
        """Тест фильтрации по несуществующему статусу"""
        result = filter_by_state(sample_transactions, "NONEXISTENT")
        assert len(result) == 0

    def test_filter_by_state_empty_list(self, empty_transactions):
        """Тест фильтрации пустого списка"""
        result = filter_by_state(empty_transactions, "EXECUTED")
        assert len(result) == 0

    @pytest.mark.parametrize("state,expected_count", [
        ("EXECUTED", 3),
        ("PENDING", 1),
        ("CANCELED", 1),
        ("NONEXISTENT", 0),
    ])
    def test_filter_by_state_parametrized(self, sample_transactions, state, expected_count):
        """Параметризованный тест для filter_by_state"""
        result = filter_by_state(sample_transactions, state)
        assert len(result) == expected_count

    def test_sort_by_date_descending(self, sample_transactions):
        """Тест сортировки по дате в порядке убывания"""
        result = sort_by_date(sample_transactions)
        dates = [item["date"] for item in result]
        assert dates == sorted(dates, reverse=True)

    def test_sort_by_date_ascending(self, sample_transactions):
        """Тест сортировки по дате в порядке возрастания"""
        result = sort_by_date(sample_transactions, ascending=True)
        dates = [item["date"] for item in result]
        assert dates == sorted(dates)

    def test_sort_by_date_same_dates(self, transactions_with_same_date):
        """Тест сортировки с одинаковыми датами"""
        result = sort_by_date(transactions_with_same_date)
        # Проверяем, что порядок сохраняется или сортировка стабильна
        dates = [item["date"] for item in result]
        assert dates == sorted(dates, reverse=True)

    def test_sort_by_date_empty_list(self, empty_transactions):
        """Тест сортировки пустого списка"""
        result = sort_by_date(empty_transactions)
        assert len(result) == 0

    def test_sort_by_date_single_item(self, sample_transactions):
        """Тест сортировки списка с одним элементом"""
        single_item = [sample_transactions[0]]
        result = sort_by_date(single_item)
        assert result == single_item

    def test_sort_by_date_missing_date_field(self):
        """Тест сортировки с отсутствующим полем даты"""
        transactions = [{"id": 1}, {"id": 2, "date": "2023-10-01T12:00:00.000000"}]
        with pytest.raises(KeyError):
            sort_by_date(transactions)

    def test_sort_by_date_invalid_date_format(self):
        """Тест сортировки с неверным форматом даты"""
        transactions = [
            {"id": 1, "date": "invalid-date-format"},
            {"id": 2, "date": "2023-10-01T12:00:00.000000"}
        ]
        with pytest.raises(ValueError):
            sort_by_date(transactions)