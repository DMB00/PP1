import pytest
from src.processing import filter_by_state, sort_by_date


def test_filter_by_state_empty_list():
    """Тест фильтрации пустого списка."""
    result = filter_by_state([], "EXECUTED")
    assert result == []


def test_filter_by_state_no_matching_state():
    """Тест фильтрации когда нет совпадений по статусу."""
    transactions = [{"state": "PENDING"}, {"state": "CANCELED"}]
    result = filter_by_state(transactions, "EXECUTED")
    assert result == []


def test_filter_by_state_missing_state_field():
    """Тест фильтрации транзакций без поля state."""
    transactions = [{"id": 1}, {"id": 2, "state": "EXECUTED"}]
    result = filter_by_state(transactions, "EXECUTED")
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_sort_by_date_empty_list():
    """Тест сортировки пустого списка."""
    result = sort_by_date([])
    assert result == []


def test_sort_by_date_single_element():
    """Тест сортировки списка с одним элементом."""
    transactions = [{"date": "2023-01-01T00:00:00.000000"}]
    result = sort_by_date(transactions)
    assert result == transactions


def test_sort_by_date_ascending_true():
    """Тест сортировки по возрастанию."""
    transactions = [
        {"date": "2023-03-01T00:00:00.000000"},
        {"date": "2023-01-01T00:00:00.000000"},
        {"date": "2023-02-01T00:00:00.000000"}
    ]
    result = sort_by_date(transactions, ascending=True)
    dates = [t["date"] for t in result]
    assert dates == ["2023-01-01T00:00:00.000000", "2023-02-01T00:00:00.000000", "2023-03-01T00:00:00.000000"]


def test_sort_by_date_ascending_false():
    """Тест сортировки по убыванию."""
    transactions = [
        {"date": "2023-01-01T00:00:00.000000"},
        {"date": "2023-03-01T00:00:00.000000"},
        {"date": "2023-02-01T00:00:00.000000"}
    ]
    result = sort_by_date(transactions, ascending=False)
    dates = [t["date"] for t in result]
    assert dates == ["2023-03-01T00:00:00.000000", "2023-02-01T00:00:00.000000", "2023-01-01T00:00:00.000000"]
