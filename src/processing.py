def filter_by_state(data: list[dict], state: str = 'EXECUTED') -> list[dict]:
    """
       Фильтрует список словарей по значению ключа 'state'.

       Args:
           data: Список словарей для фильтрации
           state: Значение для фильтрации (по умолчанию 'EXECUTED')

       Returns:
           Новый список словарей, где state соответствует указанному значению
       """
    return [item for item in data if item.get('state') == state]


def sort_by_date(data: list[dict], reverse: bool = True) -> list[dict]:
    """Сортирует список словарей по дате (по умолчанию от новых к старым)."""
    return sorted(data, key=lambda x: x['date'], reverse=reverse)