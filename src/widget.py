"""
Модуль widget содержит функции для виджета операций.
"""

from .masks import get_mask_account, get_mask_card_number


def mask_account_card(account_info: str) -> str:
    """
    Маскирует номер счета или карты в переданной строке.

    Args:
        account_info: строка с информацией о счете или карте

    Returns:
        str: строка с замаскированным номером
    """
    if not account_info:
        return ""

    if "Счет" in account_info:
        # Обработка счета
        account_number = account_info.split("Счет")[-1].strip()
        masked_number = get_mask_account(account_number)
        return f"Счет {masked_number}"
    else:
        # Обработка карты
        digits = "".join(filter(str.isdigit, account_info))
        if len(digits) == 16:
            masked_number = get_mask_card_number(digits)
            text_part = "".join(filter(lambda x: not x.isdigit(), account_info)).strip()
            return f"{text_part} {masked_number}"
        return account_info


def get_date(date_string: str) -> str:
    """
    Преобразует дату из формата ISO в формат DD.MM.YYYY.

    Args:
        date_string: дата в формате ISO

    Returns:
        str: дата в формате DD.MM.YYYY или исходная строка при ошибке
    """
    if date_string is None:
        return ""

    try:
        # Обрабатываем различные форматы
        if 'T' in date_string:
            date_part = date_string.split('T')[0]
        else:
            date_part = date_string

        # Парсим дату
        parts = date_part.split('-')
        if len(parts) == 3:
            year, month, day = parts
            return f"{int(day):02d}.{int(month):02d}.{year}"
        else:
            # Если формат не соответствует ожидаемому, возвращаем исходную строку
            return date_string

    except (ValueError, AttributeError, TypeError, IndexError):
        # При любой ошибке возвращаем исходную строку
        return date_string
