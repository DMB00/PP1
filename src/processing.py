from datetime import datetime


def filter_by_state(transactions: list, state: str) -> list:
    """Фильтрует транзакции по статусу."""
    return [t for t in transactions if t.get("state") == state]


def sort_by_date(transactions: list, ascending: bool = False) -> list:
    """Сортирует транзакции по дате."""

    def get_date_key(transaction):
        date_str = transaction.get("date", "")
        try:
            if 'T' in date_str:
                date_part = date_str.split('T')[0]
            else:
                date_part = date_str
            return datetime.strptime(date_part, "%Y-%m-%d")
        except (ValueError, TypeError):
            # Для некорректных дат возвращаем минимальную дату
            return datetime.min

    return sorted(transactions, key=get_date_key, reverse=not ascending)
