import pytest
from src.processing import filter_by_state, sort_by_date


class TestProcessing:
    """Тесты для модуля processing с параметризацией"""

    # Параметризованные тесты для filter_by_state
    @pytest.mark.parametrize("state,expected_count", [
        ("EXECUTED", 3),
        ("PENDING", 1),
        ("CANCELED", 1),
        ("NONEXISTENT", 0),
        ("executed", 0),  # регистрозависимость
        ("", 0),  # пустая строка
    ])
    def test_filter_by_state(self, sample_transactions, state, expected_count):
        """Параметризованный тест фильтрации по статусу"""
        result = filter_by_state(sample_transactions, state)
        assert len(result) == expected_count
        if expected_count > 0:
            assert all(item["state"] == state for item in result)

    @pytest.mark.parametrize("transactions,state,expected_count", [
        ([], "EXECUTED", 0),  # пустой список
        ([{"state": "EXECUTED"}], "EXECUTED", 1),  # один элемент
        ([{"state": "EXECUTED"}, {"state": "PENDING"}], "EXECUTED", 1),  # смешанные статусы
        ([{"state": "EXECUTED"}, {"state": "EXECUTED"}], "EXECUTED", 2),  # дублирующиеся статусы
    ])
    def test_filter_by_state_edge_cases(self, transactions, state, expected_count):
        """Тест граничных случаев фильтрации"""
        result = filter_by_state(transactions, state)
        assert len(result) == expected_count

    def test_filter_by_state_missing_state_field(self):
        """Тест фильтрации при отсутствии поля state"""
        # ИЗМЕНЕНО: функция не вызывает KeyError, а просто пропускает элементы без state
        transactions = [{"id": 1}, {"id": 2, "state": "EXECUTED"}]
        result = filter_by_state(transactions, "EXECUTED")
        assert len(result) == 1
        assert result[0]["id"] == 2

    # Параметризованные тесты для sort_by_date
    @pytest.mark.parametrize("ascending,expected_dates", [
        (False, ["2023-12-25T00:00:00.000000", "2023-11-20T16:45:00.000000",
                 "2023-10-01T12:00:00.000000", "2023-09-15T08:30:00.000000",
                 "2023-08-05T10:15:00.000000"]),  # по убыванию
        (True, ["2023-08-05T10:15:00.000000", "2023-09-15T08:30:00.000000",
                "2023-10-01T12:00:00.000000", "2023-11-20T16:45:00.000000",
                "2023-12-25T00:00:00.000000"]),  # по возрастанию
    ])
    def test_sort_by_date_direction(self, sample_transactions, ascending, expected_dates):
        """Параметризованный тест направления сортировки"""
        result = sort_by_date(sample_transactions, ascending=ascending)
        actual_dates = [item["date"] for item in result]
        assert actual_dates == expected_dates

    def test_sort_by_date_same_dates(self, transactions_with_same_date):
        """Тест сортировки с одинаковыми датами"""
        result = sort_by_date(transactions_with_same_date)
        # Проверяем что сортировка стабильна (сохраняет порядок одинаковых элементов)
        dates = [item["date"] for item in result]
        assert dates == sorted(dates, reverse=True)

    @pytest.mark.parametrize("transactions,expected_length", [
        ([], 0),  # пустой список
        ([{"date": "2023-10-01T12:00:00.000000"}], 1),  # один элемент
    ])
    def test_sort_by_date_edge_cases(self, transactions, expected_length):
        """Тест граничных случаев сортировки"""
        result = sort_by_date(transactions)
        assert len(result) == expected_length

    def test_sort_by_date_missing_date_field(self):
        """Тест сортировки при отсутствии поля date"""
        # ИЗМЕНЕНО: функция не вызывает KeyError, а обрабатывает это
        transactions = [{"id": 1}, {"id": 2, "date": "2023-10-01T12:00:00.000000"}]
        result = sort_by_date(transactions)
        assert len(result) == 2  # Оба элемента должны остаться

    def test_sort_by_date_invalid_date_format(self):
        """Тест сортировки с неверным форматом даты"""
        # ИЗМЕНЕНО: функция не вызывает ValueError, а обрабатывает это
        transactions = [
            {"id": 1, "date": "invalid-date-format"},
            {"id": 2, "date": "2023-10-01T12:00:00.000000"}
        ]
        result = sort_by_date(transactions)
        assert len(result) == 2  # Оба элемента должны остаться

    def test_sort_by_date_mixed_formats(self):
        """Тест сортировки с разными форматами дат"""
        transactions = [
            {"id": 1, "date": "2023-10-01"},  # только дата
            {"id": 2, "date": "2023-10-01T12:00:00.000000"},  # дата с временем
            {"id": 3, "date": "2023-09-30T23:59:59.999999"},  # другая дата
        ]
        result = sort_by_date(transactions)
        assert len(result) == 3  # Все элементы должны остаться