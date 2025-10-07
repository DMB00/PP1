"""
Модуль processing содержит функции для обработки транзакций.
"""

from datetime import datetime


def filter_by_state(transactions: list, state: str) -> list:
    """
    Фильтрует транзакции по статусу.

    Args:
        transactions: список транзакций
        state: статус для фильтрации

    Returns:
        list: отфильтрованный список
    """
    return [tx for tx in transactions if tx.get("state") == state]


def sort_by_date(transactions: list, ascending: bool = False) -> list:
    """
    Сортирует транзакции по дате.

    Args:
        transactions: список транзакций
        ascending: порядок сортировки (True - по возрастанию, False - по убыванию)

    Returns:
        list: отсортированный список
    """

    def get_date_key(transaction):
        date_str = transaction["date"]
        return datetime.fromisoformat(date_str)

    return sorted(transactions, key=get_date_key, reverse=not ascending)
