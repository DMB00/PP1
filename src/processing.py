def filter_by_state(data: list[dict], state: str = 'EXECUTED') -> list[dict]:
    return [item for item in data if item.get('state') == state]


def sort_by_date(data: list[dict], reverse: bool = True) -> list[dict]:
    return sorted(data, key=lambda x: x['date'], reverse=reverse)